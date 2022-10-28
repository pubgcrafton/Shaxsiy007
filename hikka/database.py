#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import json
import logging
import os
import time
import asyncio
import collections

try:
    import redis
except ImportError as e:
    if "RAILWAY" in os.environ:
        raise e


import typing

from telethon.tl.types import Message
from telethon.errors.rpcerrorlist import ChannelsTooMuchError

from . import utils, main
from .pointers import (
    PointerList,
    PointerDict,
)
from .types import JSONSerializable
from .tl_cache import CustomTelegramClient

DATA_DIR = (
    os.path.normpath(os.path.join(utils.get_base_dir(), ".."))
    if "OKTETO" not in os.environ and "DOCKER" not in os.environ
    else "/data"
)

logger = logging.getLogger(__name__)


class NoAssetsChannel(Exception):
    """Obyekt kanali mavjud bo‘lmagan holda obyektni o‘qish/saqlashda ko‘tariladi"""


class Database(dict):
    _next_revision_call = 0
    _revisions = []
    _assets = None
    _me = None
    _redis = None
    _saving_task = None

    def __init__(self, client: CustomTelegramClient):
        super().__init__()
        self._client = client

    def __repr__(self):
        return object.__repr__(self)

    def _redis_save_sync(self):
        with self._redis.pipeline() as pipe:
            pipe.set(
                str(self._client.tg_id),
                json.dumps(self, ensure_ascii=True),
            )
            pipe.execute()

    async def remote_force_save(self) -> bool:
        """Ma'lumotlar bazasini kutmasdan uzoq so'nggi nuqtaga saqlashga majbur qiling"""
        if not self._redis:
            return False

        await utils.run_sync(self._redis_save_sync)
        logger.debug("Redis-ga JB nashr etildi")
        return True

    async def _redis_save(self) -> bool:
        """Ma'lumotlar bazasini redis-ga saqlang"""
        if not self._redis:
            return False

        await asyncio.sleep(5)

        await utils.run_sync(self._redis_save_sync)

        logger.debug("Redis-ga JB nashr etildi")

        self._saving_task = None
        return True

    async def redis_init(self) -> bool:
        """Redis ma'lumotlar bazasini ishga tushiring"""
        if REDIS_URI := os.environ.get("REDIS_URL") or main.get_config_key("redis_uri"):
            self._redis = redis.Redis.from_url(REDIS_URI)
        else:
            return False

    async def init(self):
        """Asinxron ishga tushirish birligi"""
        if os.environ.get("REDIS_URL") or main.get_config_key("redis_uri"):
            await self.redis_init()

        self._db_path = os.path.join(DATA_DIR, f"config-{self._client.tg_id}.json")
        self.read()

        try:
            self._assets, _ = await utils.asset_channel(
                self._client,
                "shaxsiy-assets",
                "🥳 Shaxsiy userbot aktivlaringiz shu yerda saqlanadi",
                archive=True,
                avatar="https://siasky.net/ZAB5fVs3A0V9MUjzrvFRkwUn8UgN8hu-FecAgWR9GhPSQQ",
            )
        except ChannelsTooMuchError:
            self._assets = None
            logger.error(
                "Obyektlar jildini topib bo‘lmadi va/yoki yaratib bo‘lmadi\n"
                "Bu bir qancha oqibatlarga olib kelishi mumkin, masalan:\n"
                "- Ishlamaydigan aktivlar xususiyati (masalan, eslatmalar)\n"
                "- Bu xato har qayta ishga tushirishda sodir bo'ladi\n\n"
                "Buni ba'zi kanallar/guruhlarni tark etish orqali hal qilishingiz mumkin"
            )

    def read(self):
        """Ma'lumotlar bazasini o'qing va uni o'zida saqlaydi"""
        if self._redis:
            try:
                self.update(
                    **json.loads(
                        self._redis.get(
                            str(self._client.tg_id),
                        ).decode(),
                    )
                )
            except Exception:
                logger.exception("Redis maʼlumotlar bazasini oʻqishda xatolik yuz berdi")
            return

        try:
            with open(self._db_path, "r", encoding="utf-8") as f:
                self.update(**json.load(f))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.warning("Maʼlumotlar bazasini oʻqib boʻlmadi!  Yangisini yaratish...")

    def process_db_autofix(self, db: dict) -> bool:
        if not utils.is_serializable(db):
            return False

        for key, value in db.copy().items():
            if not isinstance(key, (str, int)):
                logger.warning(
                    "DbAutoFix: %s kaliti tushirildi, chunki u string yoki int emas",
                    key,
                )
                continue

            if not isinstance(value, dict):
                # If value is not a dict (module values), drop it,
                # otherwise it may cause problems
                del db[key]
                logger.warning(
                    "DbAutoFix: Dropped key %s, because it is non-dict, but %s",
                    key,
                    type(value),
                )
                continue

            for subkey in value:
                if not isinstance(subkey, (str, int)):
                    del db[key][subkey]
                    logger.warning(
                        "DbAutoFix: %s db kalitining %s pastki kaliti tushirildi, chunki bunday emas"
                        " string yoki int",
                        subkey,
                        key,
                    )
                    continue

        return True

    def save(self) -> bool:
        """Ma'lumotlar bazasini saqlash"""
        if not self.process_db_autofix(self):
            try:
                rev = self._revisions.pop()
                while not self.process_db_autofix(rev):
                    rev = self._revisions.pop()
            except IndexError:
                raise RuntimeError(
                    "Buzilgan ma'lumotlar bazasini tiklash uchun versiya topilmadi "
                    "ma'lumotlar bazasi buzilgan va muammolarga olib kelishi mumkin, "
                    "Bas, uni saqlash haromdir."
                )

            self.clear()
            self.update(**rev)

            raise RuntimeError(
                "Ma'lumotlar bazasi oxirgi versiyaga qayta yozilmoqda, chunki yangisi uni yo'q qildi"
            )

        if self._next_revision_call < time.time():
            self._revisions += [dict(self)]
            self._next_revision_call = time.time() + 3

        while len(self._revisions) > 15:
            self._revisions.pop()

        if self._redis:
            if not self._saving_task:
                self._saving_task = asyncio.ensure_future(self._redis_save())
            return True

        try:
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self, f, indent=4)
        except Exception:
            logger.exception("Maʼlumotlar bazasini saqlab boʻlmadi!")
            return False

        return True

    async def store_asset(self, message: Message) -> int:
        """
        Aktivlarni saqlang
         asset_id ni butun son sifatida qaytaradi
        """
        if not self._assets:
            raise NoAssetsChannel("Obyektni mavjud bo‘lmagan kanalga saqlashga harakat qildi")

        return (
            (await self._client.send_message(self._assets, message)).id
            if isinstance(message, Message)
            else (
                await self._client.send_message(
                    self._assets,
                    file=message,
                    force_document=True,
                )
            ).id
        )

    async def fetch_asset(self, asset_id: int) -> typing.Optional[Message]:
        """Oldin saqlangan obyektni asset_id bo‘yicha olib keling"""
        if not self._assets:
            raise NoAssetsChannel(
                "Obyektni mavjud bo‘lmagan kanaldan olishga harakat qildi"
            )

        asset = await self._client.get_messages(self._assets, ids=[asset_id])

        return asset[0] if asset else None

    def get(
        self,
        owner: str,
        key: str,
        default: typing.Optional[JSONSerializable] = None,
    ) -> JSONSerializable:
        """Ma'lumotlar bazasi kalitini oling"""
        try:
            return self[owner][key]
        except KeyError:
            return default

    def set(self, owner: str, key: str, value: JSONSerializable) -> bool:
        """Ma'lumotlar bazasi kalitini o'rnating"""
        if not utils.is_serializable(owner):
            raise RuntimeError(
                "Ob'ektni yozishga harakat qilindi "
                f"{owner=} ({type(owner)=}) ma'lumotlar bazasiga.  Emas "
                "Xatolarga olib keladigan JSON seriyali kalit"
            )

        if not utils.is_serializable(key):
            raise RuntimeError(
                "Ob'ektni yozishga harakat qilindi "
                f"{key=} ({type(key)=}) ma'lumotlar bazasiga.  Emas "
                "Xatolarga olib keladigan JSON seriyali kalit"
            )

        if not utils.is_serializable(value):
            raise RuntimeError(
                "Ob'ektini yozishga harakat qilindi "
                f"{key=} ({type(value)=}) ma'lumotlar bazasiga.  Emas "
                "Xatolarga olib keladigan JSON seriyali qiymat"
            )

        super().setdefault(owner, {})[key] = value
        return self.save()

    def pointer(
        self,
        owner: str,
        key: str,
        default: typing.Optional[JSONSerializable] = None,
    ) -> JSONSerializable:
        """Ma'lumotlar bazasi kalitiga ko'rsatgichni oling"""
        value = self.get(owner, key, default)
        mapping = {
            list: PointerList,
            dict: PointerDict,
            collections.abc.Hashable: lambda v: v,
        }

        pointer_constructor = next(
            (pointer for type_, pointer in mapping.items() if isinstance(value, type_)),
            None,
        )

        if pointer_constructor is None:
            raise ValueError(
                f"Tur uchun ko'rsatgich {type(value).__name__} amalga oshirilmaydi"
            )

        return pointer_constructor(self, owner, key, default)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hdoniyor_tm
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/emoji/344/shield-emoji.png
# meta developer: @DONIYOR_TM

import asyncio
import io
import json
import logging
import time

from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


@loader.tds
class APIRatelimiterMod(loader.Module):
    """Helps userbot avoid spamming Telegram API"""

    strings = {
        "name": "APIRatelimiter",
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>Ogohlantirish</b>\n\nHisobingiz belgilangan so'rovlar chegarasidan oshib ketdi"
            " sozlashda. Telegram API to'fonining oldini olish uchun userbot mavjud"
            " <b>to'liq muzlash</b> for {} soniyalar. Qo'shimcha ma'lumotlar ilova qilingan"
            " fayl. \n\nYordam olish tavsiya etiladi <code>{prefix}qo'llab-quvvatlash</code>"
            " guruh!\n\nAgar siz buni rejalashtirilgan xatti-harakatlar deb o'ylasangiz, kuting"
            " userbot qulfini ochadi va keyingi safar qachon ijro etasiz"
            " bunday operatsiya, foydalanish <code>{prefix}suspend_api_protect</code> &lt;time"
            " soniyalarda&gt;"
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Noto'g'ri dalillar</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API toshqindan himoya qilish"
            " uchun o'chirilgan {} soniya</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ushbu harakat amalga oshiriladi"
            " Telegram API-ni to'ldirish uchun o'z hisobingizni oching.</b> <i>Tasdiqlash uchun,"
            " haqiqatan ham nima qilayotganingizni bilsangiz, ushbu oddiy sinovni yakunlang -"
            " boshqalardan farq qiladigan emoji toping</i>"
        ),
        "on": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Himoya yoqilgan</b>"
        ),
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Himoya"
            " o'chitilgan</b>"
        ),
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ishonchingiz komilmi?</b>"
        ),
    }

    strings_ru = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>ВНИМАНИЕ!</b>\n\nАккаунт вышел за лимиты запросов, указанные в"
            " конфиге. С целью предотвращения флуда Telegram API, юзербот был"
            " <b>полностью заморожен</b> на {} секунд. Дополнительная информация"
            " прикреплена в файле ниже. \n\nРекомендуется обратиться за помощью в"
            " <code>{prefix}support</code> группу!\n\nЕсли ты считаешь, что это"
            " запланированное поведение юзербота, просто подожди, пока закончится"
            " таймер и в следующий раз, когда запланируешь выполнять такую"
            " ресурсозатратную операцию, используй"
            " <code>{prefix}suspend_api_protect</code> &lt;время в секундах&gt;"
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Неверные"
            " аргументы</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита API отключена"
            " на {} секунд</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Это действие"
            " открывает юзерботу возможность флудить Telegram API.</b> <i>Для того,"
            " чтобы убедиться, что ты действительно уверен в том, что делаешь - реши"
            " простенький тест - найди отличающийся эмодзи.</i>"
        ),
        "on": "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита включена</b>",
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита отключена</b>"
        ),
        "u_sure": "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ты уверен?</b>",
    }

    _ratelimiter = []
    _suspend_until = 0
    _lock = False

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "time_sample",
                15,
                lambda: "Vaqt namunasi YO'Q",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "threshold",
                100,
                lambda: "Darajasi YO'Q",
                validator=loader.validators.Integer(minimum=10),
            ),
            loader.ConfigValue(
                "local_floodwait",
                30,
                lambda: "Mahalliy FW YO'Q",
                validator=loader.validators.Integer(minimum=10, maximum=3600),
            ),
        )

    async def client_ready(self):
        asyncio.ensure_future(self._install_protection())

    async def _install_protection(self):
        await asyncio.sleep(30)  # Restart lock
        if hasattr(self._client._call, "_old_call_rewritten"):
            raise loader.SelfUnload("Allaqachon o'rnatilgan")

        old_call = self._client._call

        async def new_call(
            sender: "MTProtoSender",  # type: ignore
            request: "TLRequest",  # type: ignore
            ordered: bool = False,
            flood_sleep_threshold: int = None,
        ):
            if time.perf_counter() > self._suspend_until and not self.get(
                "disable_protection",
                True,
            ):
                request_name = type(request).__name__
                self._ratelimiter += [[request_name, time.perf_counter()]]

                self._ratelimiter = list(
                    filter(
                        lambda x: time.perf_counter() - x[1]
                        < int(self.config["time_sample"]),
                        self._ratelimiter,
                    )
                )

                if (
                    len(self._ratelimiter) > int(self.config["threshold"])
                    and not self._lock
                ):
                    self._lock = True
                    report = io.BytesIO(
                        json.dumps(
                            self._ratelimiter,
                            indent=4,
                        ).encode("utf-8")
                    )
                    report.name = "local_fw_report.json"

                    await self.inline.bot.send_document(
                        self.tg_id,
                        report,
                        caption=self.strings("warning").format(
                            self.config["local_floodwait"],
                            prefix=self.get_prefix(),
                        ),
                    )

                    # It is intented to use time.sleep instead of asyncio.sleep
                    time.sleep(int(self.config["local_floodwait"]))
                    self._lock = False

            return await old_call(sender, request, ordered, flood_sleep_threshold)

        self._client._call = new_call
        self._client._old_call_rewritten = old_call
        self._client._call._hikka_overwritten = True
        logger.debug("Muvaffaqiyatli o'rnatilgan  ratelimiter")

    async def on_unload(self):
        if hasattr(self._client, "_old_call_rewritten"):
            self._client._call = self._client._old_call_rewritten
            delattr(self._client, "_old_call_rewritten")
            logger.debug("Muvaffaqiyatli o'chirilgan ratelimiter")

    @loader.command(ru_doc="<время в секундах> - Заморозить защиту API на N секунд")
    async def suspend_api_protect(self, message: Message):
        """<time in seconds> - Suspend API Ratelimiter for n seconds"""
        args = utils.get_args_raw(message)

        if not args or not args.isdigit():
            await utils.answer(message, self.strings("args_invalid"))
            return

        self._suspend_until = time.perf_counter() + int(args)
        await utils.answer(message, self.strings("suspended_for").format(args))

    @loader.command(ru_doc="Включить/выключить защиту API")
    async def api_fw_protection(self, message: Message):
        """Toggle API Ratelimiter"""
        await self.inline.form(
            message=message,
            text=self.strings("u_sure"),
            reply_markup=[
                {"text": "🚫 Yo'q", "action": "close"},
                {"text": "✅ Ha", "callback": self._finish},
            ],
        )

    async def _finish(self, call: InlineCall):
        state = self.get("disable_protection", True)
        self.set("disable_protection", not state)
        await call.edit(self.strings("on" if state else "off"))

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: inline

import asyncio
import datetime
import io
import json
import logging
import time

from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import BotInlineCall

logger = logging.getLogger(__name__)


@loader.tds
class ShaxsiyBackupMod(loader.Module):
    """Automatic database backup"""

    strings = {
        "name": "ShaxsiyBackup",
        "period": (
            "🙀️️ <b>«ALFA» birligi</b> vaqti-vaqti bilan ma'lumotlar bazasining zaxira nusxalarini yaratadi. Siz qila olasiz"
            " keyinchalik bu xatti-harakatni o'zgartiring.\n\nIltimos, davriyligini tanlang"
            " avtomatlashtirilgan ma'lumotlar bazasini zaxiralash"
        ),
        "saved": (
            "✅ Zaxira muddati saqlandi. Keyinchalik uni qayta sozlashingiz mumkin"
            " .set_backup_period"
        ),
        "never": (
            "✅ Avtomatik zaxira nusxasini yaratmayman. Keyinchalik uni qayta sozlashingiz mumkin"
            " .set_backup_period"
        ),
        "invalid_args": (
            "🚫 <b>To'g'ri zaxira muddatini soat bilan belgilang yoki o'chirish uchun `0`</b>"
        ),
    }

    strings_ru = {
        "period": (
            "🙀️ <b>Юнит «ALPHA»</b> создает регулярные резервные копии. Эти настройки"
            " можно изменить позже.\n\nПожалуйста, выберите периодичность резервного"
            " копирования"
        ),
        "saved": (
            "✅ Периодичность сохранена! Ее можно изменить с помощью .set_backup_period"
        ),
        "never": (
            "✅ Я не буду делать автоматические резервные копии. Можно отменить"
            " используя .set_backup_period"
        ),
        "invalid_args": (
            "🚫 <b>Укажи правильную периодичность в часах, или `0` для отключения</b>"
        ),
    }

    async def client_ready(self):
        if not self.get("period"):
            await self.inline.bot.send_photo(
                self.tg_id,
                photo="https://siasky.net/DAADxuaSG5ZW7jJHe2GMU71xJxKpj5qwSOCQwQm6BILOrA",
                caption=self.strings("period"),
                reply_markup=self.inline.generate_markup(
                    utils.chunks(
                        [
                            {
                                "text": f"⏳ {i} h",
                                "callback": self._set_backup_period,
                                "args": (i,),
                            }
                            for i in {1, 2, 4, 6, 8, 12, 24, 48, 168}
                        ],
                        3,
                    )
                    + [
                        [
                            {
                                "text": "🚫 Hech qachon",
                                "callback": self._set_backup_period,
                                "args": (0,),
                            }
                        ]
                    ]
                ),
            )

        self._backup_channel, _ = await utils.asset_channel(
            self._client,
            "shaxsiy-backups",
            "⏱ Ma'lumotlar bazangizning zaxira nusxalari u erda paydo bo'ladi",
            silent=True,
            archive=True,
            avatar="https://siasky.net/DAADxuaSG5ZW7jJHe2GMU71xJxKpj5qwSOCQwQm6BILOrA",
            _folder="shaxsiy",
        )

        self.handler.start()

    async def _set_backup_period(self, call: BotInlineCall, value: int):
        if not value:
            self.set("period", "disabled")
            await call.answer(self.strings("never"), show_alert=True)
            await call.delete()
            return

        self.set("period", value * 60 * 60)
        self.set("last_backup", round(time.time()))

        await call.answer(self.strings("saved"), show_alert=True)
        await call.delete()

    @loader.command(ru_doc="<время в часах> - Установить частоту бэкапов")
    async def set_backup_period(self, message: Message):
        """<time in hours> - Change backup frequency"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit() or int(args) not in range(200):
            await utils.answer(message, self.strings("invalid_args"))
            return

        if not int(args):
            self.set("period", "disabled")
            await utils.answer(message, f"<b>{self.strings('never')}</b>")
            return

        period = int(args) * 60 * 60
        self.set("period", period)
        self.set("last_backup", round(time.time()))
        await utils.answer(message, f"<b>{self.strings('saved')}</b>")

    @loader.loop(interval=1)
    async def handler(self):
        try:
            if not self.get("period"):
                await asyncio.sleep(3)
                return

            if not self.get("last_backup"):
                self.set("last_backup", round(time.time()))
                await asyncio.sleep(self.get("period"))
                return

            if self.get("period") == "disabled":
                raise loader.StopLoop

            await asyncio.sleep(
                self.get("last_backup") + self.get("period") - time.time()
            )

            backup = io.BytesIO(json.dumps(self._db).encode("utf-8"))
            backup.name = (
                f"shaxsiy-db-backup-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M-%S')}.json"
            )

            await self._client.send_file(
                self._backup_channel,
                backup,
            )
            self.set("last_backup", round(time.time()))
        except loader.StopLoop:
            raise
        except Exception:
            logger.exception("ShaxsiyBackup muvaffaqiyatsiz tugadi")
            await asyncio.sleep(60)

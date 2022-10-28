#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import re
import string
from hikka.inline.types import BotInlineMessage

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class InlineStuffMod(loader.Module):
    """Ichki narsalarni qo'llab-quvvatlaydi"""

    strings = {
        "name": "InlineStuff",
        "bot_username_invalid": (
            "<emoji document_id=5415905755406539934>🚫</emoji> <b>Belgilangan bot"
            " username is invalid. It must end with </b><code>bot</code><b> and contain"
            " at least 4 symbols</b>"
        ),
        "bot_username_occupied": (
            "<emoji document_id=5415905755406539934>🚫</emoji> <b>Bu foydalanuvchi nomi"
            " allaqachon ishg'ol qilingan</b>"
        ),
        "bot_updated": (
            "<emoji document_id=6318792204118656433>🎉</emoji> <b>Muvaffaqiyatli ravishda sozlang"
            " saqlandi. O'zgarishlarni qo'llash uchun foydalanuvchini qayta ishga tushiring</b>"
        ),
        "this_is_shaxsiy": (
            "🔆 <b>Salom! Bu Shaxsiy — kuchli modulli Telegram foydalanuvchisi. Siz qila olasiz"
            " uni hisob qaydnomangizga o'rnating!</b>\n\n<b>🌍 <a"
            ' href="https://github.com/pubgcrafton/shaxsiy">GitHub</a></b>\n<b>👥 <a'
            ' href="https://t.me/shaxsiy_userbot_guruhi">Qõllab-quvvatlash</a></b>'
        ),
    }

    strings_ru = {
        "bot_username_invalid": (
            "<emoji document_id=5415905755406539934>🚫</emoji> <b>Неправильный ник"
            " бота. Он должен заканчиваться на </b><code>bot</code><b> и быть не короче"
            " чем 5 символов</b>"
        ),
        "bot_username_occupied": (
            "<emoji document_id=5415905755406539934>🚫</emoji> <b>Такой ник бота уже"
            " занят</b>"
        ),
        "bot_updated": (
            "<emoji document_id=6318792204118656433>🎉</emoji> <b>Настройки сохранены."
            " Для их применения нужно перезагрузить юзербот</b>"
        ),
        "this_is_shaxsiy": (
            "🔆 <b>Привет! Это Shaxsiy — мощный модульный Telegram юзербот. Вы можете"
            " установить его на свой аккаунт!</b>\n\n<b>🌍 <a"
            ' href="https://github.com/hikariaitama/Hikka">GitHub</a></b>\n<b>👥 <a'
            ' href="https://t.me/shaxsiy_userbot_guruhi">Чат поддержки</a></b>'
        ),
    }

    async def watcher(self, message: Message):
        if (
            getattr(message, "out", False)
            and getattr(message, "via_bot_id", False)
            and message.via_bot_id == self.inline.bot_id
            and "Ushbu xabar avtomatik ravishda o'chiriladi"
            in getattr(message, "raw_text", "")
        ):
            await message.delete()
            return

        if (
            not getattr(message, "out", False)
            or not getattr(message, "via_bot_id", False)
            or message.via_bot_id != self.inline.bot_id
            or "Galereyani ochish..." not in getattr(message, "raw_text", "")
        ):
            return

        id_ = re.search(r"#id: ([a-zA-Z0-9]+)", message.raw_text)[1]

        await message.delete()

        m = await message.respond("🔆 <b>Galereyani ochish....</b>")

        await self.inline.gallery(
            message=m,
            next_handler=self.inline._custom_map[id_]["handler"],
            caption=self.inline._custom_map[id_].get("caption", ""),
            force_me=self.inline._custom_map[id_].get("force_me", False),
            disable_security=self.inline._custom_map[id_].get(
                "disable_security", False
            ),
            silent=True,
        )

    async def _check_bot(self, username: str) -> bool:
        async with self._client.conversation("@BotFather", exclusive=False) as conv:
            try:
                m = await conv.send_message("/token")
            except YouBlockedUserError:
                await self._client(UnblockRequest(id="@BotFather"))
                m = await conv.send_message("/token")

            r = await conv.get_response()

            await m.delete()
            await r.delete()

            if not hasattr(r, "reply_markup") or not hasattr(r.reply_markup, "rows"):
                return False

            for row in r.reply_markup.rows:
                for button in row.buttons:
                    if username != button.text.strip("@"):
                        continue

                    m = await conv.send_message("/cancel")
                    r = await conv.get_response()

                    await m.delete()
                    await r.delete()

                    return True

    @loader.command(ru_doc="<юзернейм> - Изменить юзернейм инлайн бота")
    async def ch_hikka_bot(self, message: Message):
        """< foydalanuvchi nomi > - Shaxsiy onlayn bot foydalanuvchi nomini o'zgartiring"""
        args = utils.get_args_raw(message).strip("@")
        if (
            not args
            or not args.lower().endswith("bot")
            or len(args) <= 4
            or any(
                litera not in (string.ascii_letters + string.digits + "_")
                for litera in args
            )
        ):
            await utils.answer(message, self.strings("bot_username_invalid"))
            return

        try:
            await self._client.get_entity(f"@{args}")
        except ValueError:
            pass
        else:
            if not await self._check_bot(args):
                await utils.answer(message, self.strings("bot_username_occupied"))
                return

        self._db.set("hikka.inline", "custom_bot", args)
        self._db.set("hikka.inline", "bot_token", None)
        await utils.answer(message, self.strings("bot_updated"))

    async def aiogram_watcher(self, message: BotInlineMessage):
        if message.text != "/start":
            return

        await message.answer_photo(
            "https://siasky.net/jADBfWhaphoeaP5yFFNoYQ6NGqxfFXwZMfRWAjgJabEkug",
            caption=self.strings("this_is_shaxsiy"),
        )

    async def client_ready(self, client, db):
        if self.get("migrated"):
            return

        self.set("migrated", True)
        async with self._client.conversation("@BotFather") as conv:
            for msg in [
                "/cancel",
                "/setinline",
                f"@{self.inline.bot_username}",
                "user@shaxsiy:~$",
            ]:
                m = await conv.send_message(msg)
                r = await conv.get_response()

                await m.delete()
                await r.delete()

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: inline

import logging
import atexit
import random
import sys
import os

import telethon
from telethon.tl.types import Message
from telethon.tl.functions.messages import (
    GetDialogFiltersRequest,
    UpdateDialogFilterRequest,
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.utils import get_display_name

from .. import loader, main, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


def restart(*argv):
    os.execl(
        sys.executable,
        sys.executable,
        "-m",
        os.path.relpath(utils.get_base_dir()),
        *argv,
    )


@loader.tds
class HikkaSettingsMod(loader.Module):
    """Advanced settings for Shaxsiy Userbot"""

    strings = {
        "name": "ShaxsiySettings",
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Kuzatuvchilar:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Kuzatuvchilar {} yõq"
            " found</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Kuzatuvchilar {} hozir"
            " <u>disabled</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Kuzatuvchilar {} hozir"
            " <u>enabled</u></b>"
        ),
        "args": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Siz belgilashingiz kerak"
            " kuzatuvchi ismi</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Ushbu foydalanuvchi uchun NoNick"
            " is now {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Iltimos, belgilang"
            " NoNick-ni almashtirish buyrug'i</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick uchun"
            " </b><code>{}</code><b> is now {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Buyruq topilmadi</b>"
        ),
        "inline_settings": "⚙️ <b>Bu erda siz Shaxsiy userbot sozlamalarini sozlashingiz mumkin</b>",
        "confirm_update": (
            "🧭 <b>Iltimos, yangilamoqchi ekanligingizni tasdiqlang. Sizning foydalanuvchi bo'limingiz bo'ladi"
            " qayta boshlandi</b>"
        ),
        "confirm_restart": "🔄 <b>Iltimos, qayta boshlamoqchi ekanligingizni tasdiqlang</b>",
        "suggest_fs": "✅ Modullar uchun FS-ni tavsiya eting",
        "do_not_suggest_fs": "🚫 Modullar uchun FS-ni tavsiya eting",
        "use_fs": "✅ Modullar uchun har doim FS-dan foydalaning",
        "do_not_use_fs": "🚫 Modullar uchun har doim FS-dan foydalaning",
        "btn_restart": "🔄 Qayta boshlang",
        "btn_update": "🧭 Yangilash",
        "close_menu": "😌 Menyuni yoping",
        "custom_emojis": "✅ Maxsus emoji",
        "no_custom_emojis": "🚫 Maxsus emoji",
        "suggest_subscribe": "✅ Kanalga obuna bo'lishni tavsiya eting",
        "do_not_suggest_subscribe": "🚫 Kanalga obuna bo'lishni tavsiya eting",
        "private_not_allowed": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Bu buyruq bo'lishi kerak"
            " executed in chat</b>"
        ),
        "nonick_warning": (
            "Diqqat! Siz NoNick-ni standart prefiks bilan yoqdingiz! "
            "shaxsiy userbot chatlarida ovozsiz bo'lishingiz mumkin. Prefiksni o'zgartiring yoki "
            "NoNick-ni o'chirib qo'ying!"
        ),
        "reply_required": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Xabarga javob bering"
            " NoNick-ga qo'shilishi kerak bo'lgan foydalanuvchi</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Ushbu harakat shaxsiy userbotni ushbu hisobdan to'liq olib tashlaydi va bo'lmaydi"
            " reverted!</b>\n\n<i>- Shaxsiy userbot suhbatlari olib tashlanadi\n- Mashg'ulot bo'ladi"
            " tugatilib, olib tashlandi\n- Shaxsiy ichki boti olib tashlanadi</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>Shaxsiy userbotni yo'q qilishni xohlaysizmi?</b>"
        ),
        "deauth_yes": "Ishonchim komil",
        "deauth_no_1": "Ishonchim komil emas",
        "deauth_no_2": "Menga aniq emas",
        "deauth_no_3": "Javob berishga qiynalaman",
        "deauth_cancel": "🚫 Bekor qilish",
        "deauth_confirm_btn": "😢 Yo'q qilish",
        "uninstall": "😢 <b>Shaxsiy userbot õchirilmoda...</b>",
        "uninstalled": (
            "😢 <b>Shaxsiy userbot o'chirildi. Veb-interfeys hali ham faol, siz boshqasini qo'shishingiz mumkin"
            " account</b>"
        ),
        "logs_cleared": "🗑 <b>Jurnallar tozalandi</b>",
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " for these commands:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " for these users:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " for these chats:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Hech narsa yo'q"
            " show...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Ushbu buyruq sizning Shaxsiy userbot veb-interfeysingizga kirish huquqini beradi. Bu emas"
            " uni jamoat guruhlarida o'tkazish tavsiya etiladi. Unda foydalanishni ko'rib chiqing <a"
            " href='tg://openmessage?user_id={}'>Saqlangan xabarlar</a>. Tur"
            " </b><code>{}proxypass force_insecure</code><b> ushbu ogohlantirishni e'tiborsiz qoldirish</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Ushbu buyruq sizning Shaxsiy userbot veb-interfeysingizga kirish huquqini beradi. Bu emas"
            " uni jamoat guruhlarida o'tkazish tavsiya etiladi. Unda foydalanishni ko'rib chiqing <a"
            " href='tg://openmessage?user_id={}'>Saqlangan xabarlar</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Shaxsiy userbot veb-interfeysiga tunnel ochish...</b>",
        "tunnel_opened": "🎉 <b>Tunnel ochildi. Ushbu havola taxminan 1 soat davomida amal qiladi</b>",
        "web_btn": "🌍 Veb-interfeys",
        "btn_yes": "🚸 Baribir oching",
        "btn_no": "🔻 Bekor qilish",
        "lavhost_web": (
            "✌️ <b>Ushbu havola sizning lavHost-dagi Shaxsiy userbot veb-interfeysingizga olib keladi</b>\n\n<i>💡"
            " Siz belgilangan lavHost hisob ma'lumotlari yordamida avtorizatsiya qilishingiz kerak"
            " ro'yxatdan o'tkazish</i>"
        ),
        "disable_stats": "✅ Anonim statistika ruxsat beradi",
        "enable_stats": "🚫 Anonim statistika o'chirilgan",
    }

    strings_ru = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Смотрители:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Смотритель {} не"
            " найден</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Смотритель {} теперь"
            " <u>выключен</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Смотритель {} теперь"
            " <u>включен</u></b>"
        ),
        "args": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Укажи имя"
            " смотрителя</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Состояние NoNick для"
            " этого пользователя: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Укажи команду, для"
            " которой надо включить\\выключить NoNick</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Состояние NoNick для"
            " </b><code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Команда не найдена</b>"
        ),
        "inline_settings": "⚙️ <b>Здесь можно управлять настройками Hikka</b>",
        "confirm_update": "🧭 <b>Подтвердите обновление. Юзербот будет перезагружен</b>",
        "confirm_restart": "🔄 <b>Подтвердите перезагрузку</b>",
        "suggest_fs": "✅ Предлагать сохранение модулей",
        "do_not_suggest_fs": "🚫 Предлагать сохранение модулей",
        "use_fs": "✅ Всегда сохранять модули",
        "do_not_use_fs": "🚫 Всегда сохранять модули",
        "btn_restart": "🔄 Перезагрузка",
        "btn_update": "🧭 Обновление",
        "close_menu": "😌 Закрыть меню",
        "custom_emojis": "✅ Кастомные эмодзи",
        "no_custom_emojis": "🚫 Кастомные эмодзи",
        "suggest_subscribe": "✅ Предлагать подписку на канал",
        "do_not_suggest_subscribe": "🚫 Предлагать подписку на канал",
        "private_not_allowed": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Эту команду нужно"
            " выполнять в чате</b>"
        ),
        "_cls_doc": "Дополнительные настройки Shaxsiy userbot",
        "nonick_warning": (
            "Внимание! Ты включил NoNick со стандартным префиксом! "
            "Тебя могут замьютить в чатах Shaxsiy userbot. Измени префикс или "
            "отключи глобальный NoNick!"
        ),
        "reply_required": (
            "<emoji document_id=5447207618793708263>🚫</emoji> <b>Ответь на сообщение"
            " пользователя, для которого нужно включить NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Это действие полностью удалит Shaxsiy userbot с этого аккаунта! Его нельзя"
            " отменить</b>\n\n<i>- Все чаты, связанные с Shaxsiy userbot будут удалены\n- Сессия"
            " Hikka будет сброшена\n- Инлайн бот Shaxsiy userbot будет удален</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Ты точно уверен, что хочешь удалить Shaxsiy userbot?</b>",
        "deauth_yes": "Я уверен",
        "deauth_no_1": "Я не уверен",
        "deauth_no_2": "Не точно",
        "deauth_no_3": "Нет",
        "deauth_cancel": "🚫 Отмена",
        "deauth_confirm_btn": "😢 Удалить",
        "uninstall": "😢 <b>Удаляю Shaxsiy userbot...</b>",
        "uninstalled": (
            "😢 <b>Shaxsiy userbot удалена. Веб-интерфейс все еще активен, можно добавить другие"
            " аккаунты!</b>"
        ),
        "logs_cleared": "🗑 <b>Логи очищены</b>",
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих команд:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих пользователей:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих чатов:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Нечего"
            " показывать...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Эта команда дает доступ к веб-интерфейсу Shaxsiy userbot. Ее выполнение в"
            " публичных чатах является угрозой безопасности. Предпочтительно выполнять"
            " ее в <a href='tg://openmessage?user_id={}'>Избранных сообщениях</a>."
            " Выполни </b><code>{}proxypass force_insecure</code><b> чтобы отключить"
            " это предупреждение</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Эта команда дает доступ к веб-интерфейсу Shaxsiy userbot. Ее выполнение в"
            " публичных чатах является угрозой безопасности. Предпочтительно выполнять"
            " ее в <a href='tg://openmessage?user_id={}'>Избранных сообщениях</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Открываю тоннель к веб-интерфейсу Shaxsiy userbot...</b>",
        "tunnel_opened": (
            "🎉 <b>Тоннель открыт. Эта ссылка будет активна не более часа</b>"
        ),
        "web_btn": "🌍 Веб-интерфейс",
        "btn_yes": "🚸 Все равно открыть",
        "btn_no": "🔻 Закрыть",
        "lavhost_web": (
            "✌️ <b>По этой ссылке ты попадешь в веб-интерфейс Shaxsiy userbot на"
            " lavHost</b>\n\n<i>💡 Тебе нужно будет авторизоваться, используя данные,"
            " указанные при настройке lavHost</i>"
        ),
        "disable_stats": "✅ Анонимная стата разрешена",
        "enable_stats": "🚫 Анонимная стата запрещена",
    }

    def get_watchers(self) -> tuple:
        return [
            str(watcher.__self__.__class__.strings["name"])
            for watcher in self.allmodules.watchers
            if watcher.__self__.__class__.strings is not None
        ], self._db.get(main.__name__, "disabled_watchers", {})

    async def _uninstall(self, call: InlineCall):
        await call.edit(self.strings("uninstall"))

        async with self._client.conversation("@BotFather") as conv:
            for msg in [
                "/deletebot",
                f"@{self.inline.bot_username}",
                "Yes, I am totally sure.",
            ]:
                m = await conv.send_message(msg)
                r = await conv.get_response()

                logger.debug(f">> {m.raw_text}")
                logger.debug(f"<< {r.raw_text}")

                await m.delete()
                await r.delete()

        async for dialog in self._client.iter_dialogs(
            None,
            ignore_migrated=True,
        ):
            if (
                dialog.name
                in {
                    "shaxsiy-logs",
                    "shaxsiy-onload",
                    "shaxsiy-assets",
                    "shaxsiy-backups",
                    "shaxsiy-acc-switcher",
                    "silent-tags",
                }
                and dialog.is_channel
                and (
                    dialog.entity.participants_count == 1
                    or dialog.entity.participants_count == 2
                    and dialog.name in {"shaxsiy-logs", "silent-tags"}
                )
                or (
                    self._client.loader.inline.init_complete
                    and dialog.entity.id == self._client.loader.inline.bot_id
                )
            ):
                await self._client.delete_dialog(dialog.entity)

        folders = await self._client(GetDialogFiltersRequest())

        if any(folder.title == "shaxsiy" for folder in folders):
            folder_id = max(
                folders,
                key=lambda x: x.id,
            ).id

            await self._client(UpdateDialogFilterRequest(id=folder_id))

        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.CRITICAL)

        await self._client.log_out()

        await call.edit(self.strings("uninstalled"))

        if "LAVHOST" in os.environ:
            os.system("lavhost restart")
            return

        atexit.register(restart, *sys.argv[1:])
        sys.exit(0)

    async def _uninstall_confirm_step_2(self, call: InlineCall):
        await call.edit(
            self.strings("deauth_confirm_step2"),
            utils.chunks(
                list(
                    sorted(
                        [
                            {
                                "text": self.strings("deauth_yes"),
                                "callback": self._uninstall,
                            },
                            *[
                                {
                                    "text": self.strings(f"deauth_no_{i}"),
                                    "action": "close",
                                }
                                for i in range(1, 4)
                            ],
                        ],
                        key=lambda _: random.random(),
                    )
                ),
                2,
            )
            + [
                [
                    {
                        "text": self.strings("deauth_cancel"),
                        "action": "close",
                    }
                ]
            ],
        )

    @loader.owner
    @loader.command(ru_doc="Удалить Shaxsiy userbot")
    async def uninstall_hikka(self, message: Message):
        """Uninstall Shaxsiy"""
        await self.inline.form(
            self.strings("deauth_confirm"),
            message,
            [
                {
                    "text": self.strings("deauth_confirm_btn"),
                    "callback": self._uninstall_confirm_step_2,
                },
                {"text": self.strings("deauth_cancel"), "action": "close"},
            ],
        )

    @loader.command(ru_doc="Очистить логи")
    async def clearlogs(self, message: Message):
        """Clear logs"""
        for handler in logging.getLogger().handlers:
            handler.buffer = []
            handler.handledbuffer = []
            handler.tg_buff = ""

        await utils.answer(message, self.strings("logs_cleared"))

    @loader.command(ru_doc="Показать активные смотрители")
    async def watchers(self, message: Message):
        """List current watchers"""
        watchers, disabled_watchers = self.get_watchers()
        watchers = [
            f"♻️ {watcher}"
            for watcher in watchers
            if watcher not in list(disabled_watchers.keys())
        ]
        watchers += [f"💢 {k} {v}" for k, v in disabled_watchers.items()]
        await utils.answer(
            message, self.strings("watchers").format("\n".join(watchers))
        )

    @loader.command(ru_doc="<module> - Включить/выключить смотрителя в текущем чате")
    async def watcherbl(self, message: Message):
        """<module> - Toggle watcher in current chat"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        watchers, disabled_watchers = self.get_watchers()

        if args.lower() not in map(lambda x: x.lower(), watchers):
            await utils.answer(message, self.strings("mod404").format(args))
            return

        args = next((x.lower() == args.lower() for x in watchers), False)

        current_bl = [
            v for k, v in disabled_watchers.items() if k.lower() == args.lower()
        ]
        current_bl = current_bl[0] if current_bl else []

        chat = utils.get_chat_id(message)
        if chat not in current_bl:
            if args in disabled_watchers:
                for k in disabled_watchers:
                    if k.lower() == args.lower():
                        disabled_watchers[k].append(chat)
                        break
            else:
                disabled_watchers[args] = [chat]

            await utils.answer(
                message,
                self.strings("disabled").format(args) + " <b>in current chat</b>",
            )
        else:
            for k in disabled_watchers.copy():
                if k.lower() == args.lower():
                    disabled_watchers[k].remove(chat)
                    if not disabled_watchers[k]:
                        del disabled_watchers[k]
                    break

            await utils.answer(
                message,
                self.strings("enabled").format(args) + " <b>in current chat</b>",
            )

        self._db.set(main.__name__, "disabled_watchers", disabled_watchers)

    @loader.command(
        ru_doc=(
            "<модуль> - Управление глобальными правилами смотрителя\n"
            "Аргументы:\n"
            "[-c - только в чатах]\n"
            "[-p - только в лс]\n"
            "[-o - только исходящие]\n"
            "[-i - только входящие]"
        )
    )
    async def watchercmd(self, message: Message):
        """<module> - Toggle global watcher rules
        Args:
        [-c - only in chats]
        [-p - only in pm]
        [-o - only out]
        [-i - only incoming]"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("args"))

        chats, pm, out, incoming = False, False, False, False

        if "-c" in args:
            args = args.replace("-c", "").replace("  ", " ").strip()
            chats = True

        if "-p" in args:
            args = args.replace("-p", "").replace("  ", " ").strip()
            pm = True

        if "-o" in args:
            args = args.replace("-o", "").replace("  ", " ").strip()
            out = True

        if "-i" in args:
            args = args.replace("-i", "").replace("  ", " ").strip()
            incoming = True

        if chats and pm:
            pm = False
        if out and incoming:
            incoming = False

        watchers, disabled_watchers = self.get_watchers()

        if args.lower() not in [watcher.lower() for watcher in watchers]:
            return await utils.answer(message, self.strings("mod404").format(args))

        args = [watcher for watcher in watchers if watcher.lower() == args.lower()][0]

        if chats or pm or out or incoming:
            disabled_watchers[args] = [
                *(["only_chats"] if chats else []),
                *(["only_pm"] if pm else []),
                *(["out"] if out else []),
                *(["in"] if incoming else []),
            ]
            self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
            await utils.answer(
                message,
                self.strings("enabled").format(args)
                + f" (<code>{disabled_watchers[args]}</code>)",
            )
            return

        if args in disabled_watchers and "*" in disabled_watchers[args]:
            await utils.answer(message, self.strings("enabled").format(args))
            del disabled_watchers[args]
            self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
            return

        disabled_watchers[args] = ["*"]
        self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
        await utils.answer(message, self.strings("disabled").format(args))

    @loader.command(ru_doc="Включить NoNick для определенного пользователя")
    async def nonickuser(self, message: Message):
        """Allow no nickname for certain user"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("reply_required"))
            return

        u = reply.sender_id
        if not isinstance(u, int):
            u = u.user_id

        nn = self._db.get(main.__name__, "nonickusers", [])
        if u not in nn:
            nn += [u]
            nn = list(set(nn))  # skipcq: PTC-W0018
            await utils.answer(message, self.strings("user_nn").format("on"))
        else:
            nn = list(set(nn) - {u})
            await utils.answer(message, self.strings("user_nn").format("off"))

        self._db.set(main.__name__, "nonickusers", nn)

    @loader.command(ru_doc="Включить NoNick для определенного чата")
    async def nonickchat(self, message: Message):
        """Allow no nickname in certain chat"""
        if message.is_private:
            await utils.answer(message, self.strings("private_not_allowed"))
            return

        chat = utils.get_chat_id(message)

        nn = self._db.get(main.__name__, "nonickchats", [])
        if chat not in nn:
            nn += [chat]
            nn = list(set(nn))  # skipcq: PTC-W0018
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html((await message.get_chat()).title),
                    "on",
                ),
            )
        else:
            nn = list(set(nn) - {chat})
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html((await message.get_chat()).title),
                    "off",
                ),
            )

        self._db.set(main.__name__, "nonickchats", nn)

    @loader.command(ru_doc="Включить NoNick для определенной команды")
    async def nonickcmdcmd(self, message: Message):
        """Allow certain command to be executed without nickname"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_cmd"))
            return

        if args not in self.allmodules.commands:
            await utils.answer(message, self.strings("cmd404"))
            return

        nn = self._db.get(main.__name__, "nonickcmds", [])
        if args not in nn:
            nn += [args]
            nn = list(set(nn))
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    self.get_prefix() + args,
                    "on",
                ),
            )
        else:
            nn = list(set(nn) - {args})
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    self.get_prefix() + args,
                    "off",
                ),
            )

        self._db.set(main.__name__, "nonickcmds", nn)

    @loader.command(ru_doc="Показать список активных NoNick команд")
    async def nonickcmds(self, message: Message):
        """Returns the list of NoNick commands"""
        if not self._db.get(main.__name__, "nonickcmds", []):
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("cmd_nn_list").format(
                "\n".join(
                    [
                        f"▫️ <code>{self.get_prefix()}{cmd}</code>"
                        for cmd in self._db.get(main.__name__, "nonickcmds", [])
                    ]
                )
            ),
        )

    @loader.command(ru_doc="Показать список активных NoNick пользователей")
    async def nonickusers(self, message: Message):
        """Returns the list of NoNick users"""
        users = []
        for user_id in self._db.get(main.__name__, "nonickusers", []).copy():
            try:
                user = await self._client.get_entity(user_id)
            except Exception:
                self._db.set(
                    main.__name__,
                    "nonickusers",
                    list(
                        (
                            set(self._db.get(main.__name__, "nonickusers", []))
                            - {user_id}
                        )
                    ),
                )

                logger.warning(
                    f"Foydalanuvchi {user_id} noickusers ro'yxatidan olib tashlandi", exc_info=True
                )
                continue

            users += [
                "▫️ <b><a"
                f' href="tg://user?id={user_id}">{utils.escape_html(get_display_name(user))}</a></b>'
            ]

        if not users:
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("user_nn_list").format("\n".join(users)),
        )

    @loader.command(ru_doc="Показать список активных NoNick чатов")
    async def nonickchats(self, message: Message):
        """Returns the list of NoNick chats"""
        chats = []
        for chat in self._db.get(main.__name__, "nonickchats", []):
            try:
                chat_entity = await self._client.get_entity(int(chat))
            except Exception:
                self._db.set(
                    main.__name__,
                    "nonickchats",
                    list(
                        (set(self._db.get(main.__name__, "nonickchats", [])) - {chat})
                    ),
                )

                logger.warning(f"Chat {chat} nonickchats ro'yxatidan olib tashlandi")
                continue

            chats += [
                "▫️ <b><a"
                f' href="{utils.get_entity_url(chat_entity)}">{utils.escape_html(get_display_name(chat_entity))}</a></b>'
            ]

        if not chats:
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("user_nn_list").format("\n".join(chats)),
        )

    async def inline__setting(self, call: InlineCall, key: str, state: bool = False):
        if callable(key):
            key()
            telethon.extensions.html.CUSTOM_EMOJIS = not main.get_config_key(
                "disable_custom_emojis"
            )
        else:
            self._db.set(main.__name__, key, state)

        if key == "no_nickname" and state and self.get_prefix() == ".":
            await call.answer(
                self.strings("nonick_warning"),
                show_alert=True,
            )
        else:
            await call.answer("Configuration value saved!")

        await call.edit(
            self.strings("inline_settings"),
            reply_markup=self._get_settings_markup(),
        )

    async def inline__update(
        self,
        call: InlineCall,
        confirm_required: bool = False,
    ):
        if confirm_required:
            await call.edit(
                self.strings("confirm_update"),
                reply_markup=[
                    {"text": "🪂 Yangilash", "callback": self.inline__update},
                    {"text": "🚫 Bekor qilish", "action": "close"},
                ],
            )
            return

        await call.answer("Sizning foydalanuvchibotingiz yangilanmoqda...", show_alert=True)
        await call.delete()
        m = await self._client.send_message("me", f"{self.get_prefix()}update --force")
        await self.allmodules.commands["update"](m)

    async def inline__restart(
        self,
        call: InlineCall,
        confirm_required: bool = False,
    ):
        if confirm_required:
            await call.edit(
                self.strings("confirm_restart"),
                reply_markup=[
                    {"text": "🔄 Qayta yuklash", "callback": self.inline__restart},
                    {"text": "🚫 Bekor qilish", "action": "close"},
                ],
            )
            return

        await call.answer("Sizning foydalanuvchibotingiz qayta tiklanmoqda...", show_alert=True)
        await call.delete()
        await self.allmodules.commands["restart"](
            await self._client.send_message("me", f"{self.get_prefix()}restart --force")
        )

    def _get_settings_markup(self) -> list:
        return [
            [
                (
                    {
                        "text": "✅ NoNick",
                        "callback": self.inline__setting,
                        "args": (
                            "no_nickname",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "no_nickname", False)
                    else {
                        "text": "🚫 NoNick",
                        "callback": self.inline__setting,
                        "args": (
                            "no_nickname",
                            True,
                        ),
                    }
                ),
                (
                    {
                        "text": "✅ Grep",
                        "callback": self.inline__setting,
                        "args": (
                            "grep",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "grep", False)
                    else {
                        "text": "🚫 Grep",
                        "callback": self.inline__setting,
                        "args": (
                            "grep",
                            True,
                        ),
                    }
                ),
                (
                    {
                        "text": "✅ InlineLogs",
                        "callback": self.inline__setting,
                        "args": (
                            "inlinelogs",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "inlinelogs", True)
                    else {
                        "text": "🚫 InlineLogs",
                        "callback": self.inline__setting,
                        "args": (
                            "inlinelogs",
                            True,
                        ),
                    }
                ),
            ],
            [
                {
                    "text": self.strings("do_not_suggest_fs"),
                    "callback": self.inline__setting,
                    "args": (
                        "disable_modules_fs",
                        False,
                    ),
                }
                if self._db.get(main.__name__, "disable_modules_fs", False)
                else {
                    "text": self.strings("suggest_fs"),
                    "callback": self.inline__setting,
                    "args": (
                        "disable_modules_fs",
                        True,
                    ),
                }
            ],
            [
                (
                    {
                        "text": self.strings("use_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "permanent_modules_fs",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "permanent_modules_fs", False)
                    else {
                        "text": self.strings("do_not_use_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "permanent_modules_fs",
                            True,
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("suggest_subscribe"),
                        "callback": self.inline__setting,
                        "args": (
                            "suggest_subscribe",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "suggest_subscribe", True)
                    else {
                        "text": self.strings("do_not_suggest_subscribe"),
                        "callback": self.inline__setting,
                        "args": (
                            "suggest_subscribe",
                            True,
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("no_custom_emojis"),
                        "callback": self.inline__setting,
                        "args": (
                            lambda: main.save_config_key(
                                "disable_custom_emojis", False
                            ),
                        ),
                    }
                    if main.get_config_key("disable_custom_emojis")
                    else {
                        "text": self.strings("custom_emojis"),
                        "callback": self.inline__setting,
                        "args": (
                            lambda: main.save_config_key("disable_custom_emojis", True),
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("disable_stats"),
                        "callback": self.inline__setting,
                        "args": ("stats", False),
                    }
                    if self._db.get(main.__name__, "stats", True)
                    else {
                        "text": self.strings("enable_stats"),
                        "callback": self.inline__setting,
                        "args": (
                            "stats",
                            True,
                        ),
                    }
                ),
            ],
            [
                {
                    "text": self.strings("btn_restart"),
                    "callback": self.inline__restart,
                    "args": (True,),
                },
                {
                    "text": self.strings("btn_update"),
                    "callback": self.inline__update,
                    "args": (True,),
                },
            ],
            [{"text": self.strings("close_menu"), "action": "close"}],
        ]

    @loader.owner
    @loader.command(ru_doc="Показать настройки")
    async def settings(self, message: Message):
        """Sozlamalar menyusini ko'rsatish"""
        await self.inline.form(
            self.strings("inline_settings"),
            message=message,
            reply_markup=self._get_settings_markup(),
        )

    @loader.owner
    @loader.command(ru_doc="Открыть тоннель к веб-интерфейсу Shaxsiy userbot")
    async def weburl(self, message: Message, force: bool = False):
        """Shaxsiy veb-interfeysingizga veb-tunnelni ochadi"""
        if "LAVHOST" in os.environ:
            form = await self.inline.form(
                self.strings("lavhost_web"),
                message=message,
                reply_markup={
                    "text": self.strings("web_btn"),
                    "url": await main.hikka.web.get_url(proxy_pass=False),
                },
                gif="https://t.me/shaxsiy_userbot/2",
            )
            return

        if (
            not force
            and not message.is_private
            and "force_insecure" not in message.raw_text.lower()
        ):
            try:
                if not await self.inline.form(
                    self.strings("privacy_leak_nowarn").format(self._client.tg_id),
                    message=message,
                    reply_markup=[
                        {
                            "text": self.strings("btn_yes"),
                            "callback": self.weburl,
                            "args": (True,),
                        },
                        {"text": self.strings("btn_no"), "action": "close"},
                    ],
                    gif="https://i.gifer.com/embedded/download/Z5tS.gif",
                ):
                    raise Exception
            except Exception:
                await utils.answer(
                    message,
                    self.strings("privacy_leak").format(
                        self._client.tg_id,
                        self.get_prefix(),
                    ),
                )

            return

        if force:
            form = message
            await form.edit(
                self.strings("opening_tunnel"),
                reply_markup={"text": "🕔 Kuting...", "data": "empty"},
                gif=(
                    "https://i.gifer.com/origin/e4/e43e1b221fd960003dc27d2f2f1b8ce1.gif"
                ),
            )
        else:
            form = await self.inline.form(
                self.strings("opening_tunnel"),
                message=message,
                reply_markup={"text": "🕔 Kuting...", "data": "empty"},
                gif=(
                    "https://i.gifer.com/origin/e4/e43e1b221fd960003dc27d2f2f1b8ce1.gif"
                ),
            )

        url = await main.hikka.web.get_url(proxy_pass=True)

        await form.edit(
            self.strings("tunnel_opened"),
            reply_markup={"text": self.strings("web_btn"), "url": url},
            gif="https://t.me/shaxsiy_userbot/2",
        )

    @loader.loop(interval=1, autostart=True)
    async def loop(self):
        obj = self.allmodules.get_approved_channel
        if not obj:
            return

        channel, event = obj

        try:
            await self._client(JoinChannelRequest(channel))
        except Exception:
            logger.exception("Kanalga qo'shilmadi")
            event.status = False
            event.set()
        else:
            event.status = True
            event.set()

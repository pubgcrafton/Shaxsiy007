#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import inspect
import logging
import os
import random
import time
from io import BytesIO
import typing

from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights, Message

from .. import loader, main, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

DEBUG_MODS_DIR = os.path.join(utils.get_base_dir(), "debug_modules")

if not os.path.isdir(DEBUG_MODS_DIR):
    os.mkdir(DEBUG_MODS_DIR, mode=0o755)

for mod in os.scandir(DEBUG_MODS_DIR):
    os.remove(mod.path)


@loader.tds
class TestMod(loader.Module):
    """Perform operations based on userbot self-testing"""

    _memory = {}

    strings = {
        "name": "Tester",
        "set_loglevel": "🚫 <b>Batafsillikni butun son yoki qator sifatida belgilang</b>",
        "no_logs": "ℹ️ <b>Sizda og'zaki so'zlashuv jurnallari yo'q {}.</b>",
        "logs_filename": "shaxsiy-logs.txt",
        "logs_caption": (
            "<emoji document_id=5188377234380954537>🔆</emoji> <b>Shaxsiy userbot bilan qaydlar"
            " fe'llik </b><code>{}</code>\n\n<emoji"
            " document_id=5454390891466726015>👋</emoji> <b>Shaxsiy userbot versiyasi:"
            " {}.{}.{}</b>{}\n<emoji document_id=6321050180095313397>⏱</emoji>"
            " <b>Bo'sh vaqt: {}</b>\n<b>{}</b>\n\n<b>{} NoNick</b>\n<b>{} Grep</b>\n<b>{}"
            " OnlineJurnallar</b>"
        ),
        "suspend_invalid_time": (
            "<emoji document_id=5416024721705673488>💀</emoji> <b>Noto‘g‘ri vaqt"
            " to'xtatib turish</b>"
        ),
        "suspended": (
            "<emoji document_id=5452023368054216810>🥶</emoji> <b>Bot to'xtatildi"
            " for</b> <code>{}</code> <b>soniya</b>"
        ),
        "results_ping": (
            "<emoji document_id=6321050180095313397>⏱</emoji> <b>Telegram ping:</b>"
            " <code>{}</code> <b>ms</b>\n<emoji"
            " document_id=5377371691078916778>😎</emoji> <b>Bo'sh vaqt: {}</b>"
        ),
        "ping_hint": (
            "<emoji document_id=5472146462362048818>💡</emoji> <i>Telegram ping asosan"
            " Telegram serverlarining kechikishi va boshqa tashqi omillarga bog'liq va mavjud"
            " foydalanuvchi userboti bo'lgan server parametrlariga hech qanday aloqasi yo'q"
            " o'rnatilgan</i>"
        ),
        "confidential": (
            "⚠️ <b> Jurnal darajasi</b><code>{}</code><b> maxfiy ma'lumotlaringizni oshkor qilishi mumkin,"
            " ehtiyot bo'ling</b>"
        ),
        "confidential_text": (
            "⚠️ <b>Log level </b><code>{0}</code><b> may reveal your confidential info,"
            " be careful</b>\n<b>Type </b><code>.logs {0} force_insecure</code><b> to"
            " ignore this warning</b>"
        ),
        "choose_loglevel": "💁‍♂️ <b>Jurnal darajasini tanlang</b>",
        "bad_module": "🚫 <b>Modullar topilmadi</b>",
        "debugging_enabled": (
            "🧑‍💻 <b>Debugging mode enabled for module </b><code>{0}</code>\n<i>Go to"
            " directory named `debug_modules`, edit file named `{0}.py` and see changes"
            " in real time</i>"
        ),
        "debugging_disabled": "✅ <b>Nosozliklarni tuzatish</b>",
    }

    strings_ru = {
        "set_loglevel": "🚫 <b>Укажи уровень логов числом или строкой</b>",
        "no_logs": "ℹ️ <b>У тебя нет логов уровня {}.</b>",
        "logs_filename": "shaxsiy-logs.txt",
        "logs_caption": (
            "<emoji document_id=5188377234380954537>🔆</emoji> <b>Логи Shaxsiy уровня"
            " </b><code>{}</code>\n\n<emoji document_id=5454390891466726015>👋</emoji>"
            " <b>Версия Shaxsiy: {}.{}.{}</b>{}\n<emoji"
            " document_id=6321050180095313397>⏱</emoji> <b>Uptime:"
            " {}</b>\n<b>{}</b>\n\n<b>{} NoNick</b>\n<b>{} Grep</b>\n<b>{}"
            " InlineLogs</b>"
        ),
        "bad_module": "🚫 <b>Модуль не найден</b>",
        "debugging_enabled": (
            "🧑‍💻 <b>Режим разработчика включен для модуля"
            " </b><code>{0}</code>\n<i>Отправляйся в директорию `debug_modules`,"
            " изменяй файл `{0}.py`, и смотри изменения в режиме реального времени</i>"
        ),
        "debugging_disabled": "✅ <b>Режим разработчика выключен</b>",
        "suspend_invalid_time": (
            "<emoji document_id=5416024721705673488>💀</emoji> <b>Неверное время"
            " заморозки</b>"
        ),
        "suspended": (
            "<emoji document_id=5452023368054216810>🥶</emoji> <b>Бот заморожен на</b>"
            " <code>{}</code> <b>секунд</b>"
        ),
        "results_ping": (
            "<emoji document_id=6321050180095313397>⏱</emoji> <b>Скорость отклика"
            " Telegram:</b> <code>{}</code> <b>ms</b>\n<emoji"
            " document_id=5377371691078916778>😎</emoji> <b>Прошло с последней"
            " перезагрузки: {}</b>"
        ),
        "ping_hint": (
            "<emoji document_id=5472146462362048818>💡</emoji> <i>Скорость отклика"
            " Telegram в большей степени зависит от загруженности серверов Telegram и"
            " других внешних факторов и никак не связана с параметрами сервера, на"
            " который установлен юзербот</i>"
        ),
        "confidential": (
            "⚠️ <b>Уровень логов </b><code>{}</code><b> может содержать личную"
            " информацию, будь осторожен</b>"
        ),
        "confidential_text": (
            "⚠️ <b>Уровень логов </b><code>{0}</code><b> может содержать личную"
            " информацию, будь осторожен</b>\n<b>Напиши </b><code>.logs {0}"
            " force_insecure</code><b>, чтобы отправить логи игнорируя"
            " предупреждение</b>"
        ),
        "choose_loglevel": "💁‍♂️ <b>Выбери уровень логов</b>",
        "_cmd_doc_dump": "Показать информацию о сообщении",
        "_cmd_doc_logs": (
            "<уровень> - Отправляет лог-файл. Уровни ниже WARNING могут содержать"
            " личную инфомрацию."
        ),
        "_cmd_doc_suspend": "<время> - Заморозить бота на некоторое время",
        "_cmd_doc_ping": "Проверяет скорость отклика юзербота",
        "_cls_doc": "Операции, связанные с самотестированием",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "force_send_all",
                False,
                "⚠️ Agar nima qilayotganini bilmasangiz, tegmang!\nOdatiy bo'lib, Shaxsiy"
                " qaysi mijoz jurnallarni keltirib chiqarganligini aniqlashga harakat qiladi. Masalan a bor"
                " TestModule moduli Client1 va TestModule2-ga Client2-da o'rnatilgan. Bo‘lardi"
                " standart, Client2 TestModule2-dan jurnallarni oladi va Client1-ni oladi"
                " TestModule-dan jurnallar. Agar ushbu parametr yoqilgan bo'lsa, Shaxsiy Userbot barchasini yuboradi"
                " Client1 va Client2-ga kirishadi, garchi u sabab bo'lmagan bo'lsa ham"
                " jurnal.",
                validator=loader.validators.Boolean(),
                on_change=self._pass_config_to_logger,
            ),
            loader.ConfigValue(
                "tglog_level",
                "INFO",
                "⚠️ Agar nima qilayotganini bilmasangiz, tegmang!\n"
                "Telegramda yuboriladigan yozuvlar uchun minimal jurnal.",
                validator=loader.validators.Choice(
                    ["INFO", "WARNING", "ERROR", "CRITICAL"]
                ),
                on_change=self._pass_config_to_logger,
            ),
        )

    def _pass_config_to_logger(self):
        logging.getLogger().handlers[0].force_send_all = self.config["force_send_all"]
        logging.getLogger().handlers[0].tg_level = self.config["tglog_level"]

    @loader.command(ru_doc="Ответь на сообщение, чтобы показать его дамп")
    async def dump(self, message: Message):
        """Use in reply to get a dump of a message"""
        if not message.is_reply:
            return

        await utils.answer(
            message,
            "<code>"
            + utils.escape_html((await message.get_reply_message()).stringify())
            + "</code>",
        )

    @loader.loop(interval=1)
    async def watchdog(self):
        if not os.path.isdir(DEBUG_MODS_DIR):
            return

        try:
            for module in os.scandir(DEBUG_MODS_DIR):
                last_modified = os.stat(module.path).st_mtime
                cls_ = module.path.split("/")[-1].split(".py")[0]

                if cls_ not in self._memory:
                    self._memory[cls_] = last_modified
                    continue

                if self._memory[cls_] == last_modified:
                    continue

                self._memory[cls_] = last_modified
                logger.debug(f"Tuzatish modulini qayta yuklash { cls_ }")
                with open(module.path, "r") as f:
                    try:
                        await next(
                            module
                            for module in self.allmodules.modules
                            if module.__class__.__name__ == "LoaderMod"
                        ).load_module(
                            f.read(),
                            None,
                            save_fs=False,
                        )
                    except Exception:
                        logger.exception("Qo‘riqchi modulini qayta yuklash amalga oshmadi")
        except Exception:
            logger.exception("Nosozliklarni tuzatib bo‘lmadi")
            return

    @loader.command(
        ru_doc=(
            "[модуль] - Для разработчиков: открыть модуль в режиме дебага и применять"
            " изменения из него в режиме реального времени"
        )
    )
    async def debugmod(self, message: Message):
        """[module] - For developers: Open module for debugging
        You will be able to track changes in real-time"""
        args = utils.get_args_raw(message)
        instance = None
        for module in self.allmodules.modules:
            if (
                module.__class__.__name__.lower() == args.lower()
                or module.strings["name"].lower() == args.lower()
            ):
                if os.path.isfile(
                    os.path.join(
                        DEBUG_MODS_DIR,
                        f"{module.__class__.__name__}.py",
                    )
                ):
                    os.remove(
                        os.path.join(
                            DEBUG_MODS_DIR,
                            f"{module.__class__.__name__}.py",
                        )
                    )

                    try:
                        delattr(module, "shaxsiy_debug")
                    except AttributeError:
                        pass

                    await utils.answer(message, self.strings("debugging_disabled"))
                    return

                module.shaxsiy_debug = True
                instance = module
                break

        if not instance:
            await utils.answer(message, self.strings("bad_module"))
            return

        with open(
            os.path.join(
                DEBUG_MODS_DIR,
                f"{instance.__class__.__name__}.py",
            ),
            "wb",
        ) as f:
            f.write(inspect.getmodule(instance).__loader__.data)

        await utils.answer(
            message,
            self.strings("debugging_enabled").format(instance.__class__.__name__),
        )

    @loader.command(ru_doc="<уровень> - Показать логи")
    async def logs(
        self,
        message: typing.Union[Message, InlineCall],
        force: bool = False,
        lvl: typing.Union[int, None] = None,
    ):
        """<level> - Dump logs"""
        if not isinstance(lvl, int):
            args = utils.get_args_raw(message)
            try:
                try:
                    lvl = int(args.split()[0])
                except ValueError:
                    lvl = getattr(logging, args.split()[0].upper(), None)
            except IndexError:
                lvl = None

        if not isinstance(lvl, int):
            try:
                if not self.inline.init_complete or not await self.inline.form(
                    text=self.strings("choose_loglevel"),
                    reply_markup=[
                        [
                            {
                                "text": "🚨 Tanqidiy",
                                "callback": self.logs,
                                "args": (False, 50),
                            },
                            {
                                "text": "🚫 Xato",
                                "callback": self.logs,
                                "args": (False, 40),
                            },
                        ],
                        [
                            {
                                "text": "⚠️ Ogohlantirish",
                                "callback": self.logs,
                                "args": (False, 30),
                            },
                            {
                                "text": "ℹ️ Ma'lumot",
                                "callback": self.logs,
                                "args": (False, 20),
                            },
                        ],
                        [
                            {
                                "text": "🧑‍💻 Tuzatish",
                                "callback": self.logs,
                                "args": (False, 10),
                            },
                            {
                                "text": "👁 Hammasi",
                                "callback": self.logs,
                                "args": (False, 0),
                            },
                        ],
                        [{"text": "🚫 Bekor qilish", "action": "close"}],
                    ],
                    message=message,
                ):
                    raise
            except Exception:
                await utils.answer(message, self.strings("set_loglevel"))

            return

        logs = "\n\n".join(
            [
                "\n".join(
                    handler.dumps(lvl, client_id=self._client.tg_id)
                    if "client_id" in inspect.signature(handler.dumps).parameters
                    else handler.dumps(lvl)
                )
                for handler in logging.getLogger().handlers
            ]
        )

        named_lvl = (
            lvl
            if lvl not in logging._levelToName
            else logging._levelToName[lvl]  # skipcq: PYL-W0212
        )

        if (
            lvl < logging.WARNING
            and not force
            and (
                not isinstance(message, Message)
                or "force_insecure" not in message.raw_text.lower()
            )
        ):
            try:
                if not self.inline.init_complete:
                    raise

                cfg = {
                    "text": self.strings("confidential").format(named_lvl),
                    "reply_markup": [
                        {
                            "text": "📤 Baribir yuboring",
                            "callback": self.logs,
                            "args": [True, lvl],
                        },
                        {"text": "🚫 Bekor qilish", "action": "close"},
                    ],
                }
                if isinstance(message, Message):
                    if not await self.inline.form(**cfg, message=message):
                        raise
                else:
                    await message.edit(**cfg)
            except Exception:
                await utils.answer(
                    message,
                    self.strings("confidential_text").format(named_lvl),
                )

            return

        if len(logs) <= 2:
            if isinstance(message, Message):
                await utils.answer(message, self.strings("no_logs").format(named_lvl))
            else:
                await message.edit(self.strings("no_logs").format(named_lvl))
                await message.unload()

            return

        if btoken := self._db.get("shaxsiy.inline", "bot_token", False):
            logs = logs.replace(
                btoken,
                f'{btoken.split(":")[0]}:***************************',
            )

        if shaxsiy_token := self._db.get("ShaxsiyDL", "token", False):
            logs = logs.replace(
                shaxsiy_token,
                f'{shaxsiy_token.split("_")[0]}_********************************',
            )

        if shaxsiy_token := self._db.get("Kirito", "token", False):
            logs = logs.replace(
                shaxsiy_token,
                f'{shaxsiy_token.split("_")[0]}_********************************',
            )

        if os.environ.get("DATABASE_URL"):
            logs = logs.replace(
                os.environ.get("DATABASE_URL"),
                "postgre://**************************",
            )

        if os.environ.get("REDIS_URL"):
            logs = logs.replace(
                os.environ.get("REDIS_URL"),
                "postgre://**************************",
            )

        if os.environ.get("shaxsiy_session"):
            logs = logs.replace(
                os.environ.get("shaxsiy_session"),
                "StringSession(**************************)",
            )

        logs = BytesIO(logs.encode("utf-16"))
        logs.name = self.strings("logs_filename")

        ghash = utils.get_git_hash()

        other = (
            *main.__version__,
            " <i><a"
            f' href="https://github.com/pubgcrafton/shaxsiy/commit/{ghash}">({ghash[:8]})</a></i>'
            if ghash
            else "",
            utils.formatted_uptime(),
            utils.get_named_platform(),
            "✅" if self._db.get(main.__name__, "no_nickname", False) else "🚫",
            "✅" if self._db.get(main.__name__, "grep", False) else "🚫",
            "✅" if self._db.get(main.__name__, "inlinelogs", False) else "🚫",
        )

        if getattr(message, "out", True):
            await message.delete()

        if isinstance(message, Message):
            await utils.answer(
                message,
                logs,
                caption=self.strings("logs_caption").format(named_lvl, *other),
            )
        else:
            await self._client.send_file(
                message.form["chat"],
                logs,
                caption=self.strings("logs_caption").format(named_lvl, *other),
            )

    @loader.owner
    @loader.command(ru_doc="<время> - Заморозить бота на N секунд")
    async def suspend(self, message: Message):
        """<time> - Suspends the bot for N seconds"""
        try:
            time_sleep = float(utils.get_args_raw(message))
            await utils.answer(
                message,
                self.strings("suspended").format(time_sleep),
            )
            time.sleep(time_sleep)
        except ValueError:
            await utils.answer(message, self.strings("suspend_invalid_time"))

    @loader.command(ru_doc="Проверить скорость отклика юзербота")
    async def ping(self, message: Message):
        """Test your userbot ping"""
        start = time.perf_counter_ns()
        message = await utils.answer(message, "<code>🐻 Kuting...</code>")

        await utils.answer(
            message,
            self.strings("results_ping").format(
                round((time.perf_counter_ns() - start) / 10**6, 3),
                utils.formatted_uptime(),
            )
            + (
                ("\n\n" + self.strings("ping_hint"))
                if random.choice([0, 0, 1]) == 1
                else ""
            ),
        )

    async def client_ready(self):
        chat, is_new = await utils.asset_channel(
            self._client,
            "shaxsiy-logs",
            "🔆 Sizning Shaxsiy jurnallaringiz ushbu suhbatda paydo bo'ladi",
            silent=True,
            avatar="",
        )

        self._logchat = int(f"-100{chat.id}")

        self.watchdog.start()

        if not is_new and any(
            participant.id == self.inline.bot_id
            for participant in (await self._client.get_participants(chat, limit=3))
        ):
            logging.getLogger().handlers[0].install_tg_log(self)
            logger.debug("Botlarni ro'yxatga olish uchun o'rnatilgan %s", self._logchat)
            return

        logger.debug("Yangi jurnal chat yaratildi, sozlash...")

        try:
            await self._client(InviteToChannelRequest(chat, [self.inline.bot_username]))
        except Exception:
            logger.warning("Suhbatga jurnalni taklif qilib bo'lmadi")

        try:
            await self._client(
                EditAdminRequest(
                    channel=chat,
                    user_id=self.inline.bot_username,
                    admin_rights=ChatAdminRights(ban_users=True),
                    rank="Logger",
                )
            )
        except Exception:
            pass

        logging.getLogger().handlers[0].install_tg_log(self)
        logger.debug("Botlarni ro'yxatga olish uchun o'rnatilgan %s", self._logchat)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import difflib
import inspect
import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class HelpMod(loader.Module):
    """Help modullar va buyruqlar uchun ko'rsatiladi"""

    strings = {
        "name": "Help",
        "bad_module": "<b>🚫 <b>Modul</b> <code>{}</code> <b>topilmadi</b>",
        "single_mod_header": (
            "<emoji document_id=5188377234380954537>🌑</emoji> <b>{}</b>:"
        ),
        "single_cmd": "\n▫️️ <code>{}{}</code> {}",
        "undoc_cmd": "🦥 Hujjatlar yo‘q",
        "all_header": (
            "<emoji document_id=5188377234380954537>🏕️</emoji> <b>{} ta modul mavjud,"
            " {} ta yashirin:</b>"
        ),
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "🚫 <b>Yashirish uchun modulni belgilang</b>",
        "hidden_shown": (
            "<emoji document_id=5188377234380954537>🌘</emoji> <b>{} modullarni yashirin,"
            " {} ko'rsatilgan modullar:</b>\n{}\n{}"
        ),
        "ihandler": "\n🎹 <code>{}</code> {}",
        "undoc_ihandler": "🦥 Hujjatlar yo‘q",
        "support": (
            "{} <b>Bog'lanish </b><a href='https://t.me/shaxsiy_userbot_guruhi'>Qo'llab-quvvatlash</a>"
        ),
        "partial_load": (
            "<emoji document_id=5472105307985419058>☝️</emoji> <b>Userbot emas"
            " to'liq yuklangan, shuning uchun barcha modullar ko'rsatilmagan</b>"
        ),
        "not_exact": (
            "<emoji document_id=5472105307985419058>☝️</emoji> <b>Aniq moslik yo'q"
            " sodir bo'ldi, shuning uchun uning o'rniga eng yaqin natija ko'rsatiladi</b>"
        ),
        "request_join": "Siz Shaxsiy qo'llab-quvvatlash suhbatiga havolani so'radingiz",
    }

    strings_ru = {
        "bad_module": "<b>🚫 <b>Модуль</b> <code>{}</code> <b>не найден</b>",
        "single_mod_header": (
            "<emoji document_id=5188377234380954537>🌑</emoji> <b>{}</b>:"
        ),
        "single_cmd": "\n▫️ <code>{}{}</code> {}",
        "undoc_cmd": "🦥 Нет описания",
        "all_header": (
            "<emoji document_id=5188377234380954537>🏕️</emoji> <b>{} модулей доступно,"
            " {} скрыто:</b>"
        ),
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "🚫 <b>Укажи модуль(-и), которые нужно скрыть</b>",
        "hidden_shown": (
            "<emoji document_id=5188377234380954537>🌘</emoji> <b>{} модулей скрыто,"
            " {} модулей показано:</b>\n{}\n{}"
        ),
        "ihandler": "\n🎹 <code>{}</code> {}",
        "undoc_ihandler": "🦥 Нет описания",
        "support": (
            "{} <b>Ссылка на </b><a href='https://t.me/shaxsiy_userbot_guruhi'>чат помощи</a>"
        ),
        "_cls_doc": "Показывает помощь по модулям",
        "partial_load": (
            "<emoji document_id=5472105307985419058>☝️</emoji> <b>Юзербот еще не"
            " загрузился полностью, поэтому показаны не все модули</b>"
        ),
        "not_exact": (
            "<emoji document_id=5472105307985419058>☝️</emoji> <b>Точного совпадения"
            " не нашлось, поэтому было выбрано наиболее подходящее</b>"
        ),
        "request_join": "Вы запросили ссылку на чат помощи Shaxsiy userbot",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "yadro_emoji",
                "▪️",
                lambda: "Asosiy modul o'qi",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "shaxsiy_emoji",
                "🧑‍🎤",
                lambda: "Shaxsiy userbot modul o'qi",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "tekis_emoji",
                "▫️",
                lambda: "Oddiy modul o'qi",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "bo'sh_emoji",
                "👁‍🗨",
                lambda: "Bo'sh modullar o'qi",
                validator=loader.validators.String(length=1),
            ),
        )

    @loader.command(
        ru_doc=(
            "<модуль или модули> - Спрятать модуль(-и) из помощи\n*Разделяй модули"
            " пробелами"
        )
    )
    async def helphide(self, message: Message):
        """<modul yoki modullar> - modul(larni)ni help buyruğidan yashirish
        *Modullarni bo'shliqlarga ajratish,"""
        modules = utils.get_args(message)
        if not modules:
            await utils.answer(message, self.strings("no_mod"))
            return

        mods = [
            i.strings["name"]
            for i in self.allmodules.modules
            if hasattr(i, "strings") and "name" in i.strings
        ]

        modules = list(filter(lambda module: module in mods, modules))
        currently_hidden = self.get("hide", [])
        hidden, shown = [], []
        for module in modules:
            if module in currently_hidden:
                currently_hidden.remove(module)
                shown += [module]
            else:
                currently_hidden += [module]
                hidden += [module]

        self.set("hide", currently_hidden)

        await utils.answer(
            message,
            self.strings("hidden_shown").format(
                len(hidden),
                len(shown),
                "\n".join([f"👁‍🗨 <i>{m}</i>" for m in hidden]),
                "\n".join([f"👁 <i>{m}</i>" for m in shown]),
            ),
        )

    async def modhelp(self, message: Message, args: str):
        exact = True
        module = self.lookup(args)

        if not module:
            _args = args.lower()
            _args = _args[1:] if _args.startswith(self.get_prefix()) else _args
            if _args in self.allmodules.commands:
                module = self.allmodules.commands[_args].__self__

        if not module:
            module = self.lookup(
                next(
                    (
                        reversed(
                            sorted(
                                [
                                    module.strings["name"]
                                    for module in self.allmodules.modules
                                ],
                                key=lambda x: difflib.SequenceMatcher(
                                    None,
                                    args.lower(),
                                    x,
                                ).ratio(),
                            )
                        )
                    ),
                    None,
                )
            )

            exact = False

        try:
            name = module.strings("name")
        except KeyError:
            name = getattr(module, "name", "XATO")

        _name = (
            f"{utils.escape_html(name)} (v{module.__version__[0]}.{module.__version__[1]}.{module.__version__[2]})"
            if hasattr(module, "__version__")
            else utils.escape_html(name)
        )

        reply = self.strings("single_mod_header").format(_name)
        if module.__doc__:
            reply += "<i>\nℹ️ " + utils.escape_html(inspect.getdoc(module)) + "\n</i>"

        commands = {
            name: func
            for name, func in module.commands.items()
            if await self.allmodules.check_security(message, func)
        }

        if hasattr(module, "inline_handlers"):
            for name, fun in module.inline_handlers.items():
                reply += self.strings("ihandler").format(
                    f"@{self.inline.bot_username} {name}",
                    (
                        utils.escape_html(inspect.getdoc(fun))
                        if fun.__doc__
                        else self.strings("undoc_ihandler")
                    ),
                )

        for name, fun in commands.items():
            reply += self.strings("single_cmd").format(
                self.get_prefix(),
                name,
                (
                    utils.escape_html(inspect.getdoc(fun))
                    if fun.__doc__
                    else self.strings("undoc_cmd")
                ),
            )

        await utils.answer(
            message, f"{reply}\n\n{'' if exact else self.strings('not_exact')}"
        )

    @loader.unrestricted
    @loader.command(ru_doc="[модуль] [-f] - Показать помощь")
    async def help(self, message: Message):
        """[modul] [-f] - Yordam ko'rsatish"""
        args = utils.get_args_raw(message)
        force = False
        if "-f" in args:
            args = args.replace(" -f", "").replace("-f", "")
            force = True

        if args:
            await self.modhelp(message, args)
            return

        count = 0
        for i in self.allmodules.modules:
            try:
                if i.commands or i.inline_handlers:
                    count += 1
            except Exception:
                pass

        hidden = self.get("hide", [])

        reply = self.strings("all_header").format(count, 0 if force else len(hidden))
        shown_warn = False

        plain_ = []
        core_ = []
        inline_ = []
        no_commands_ = []

        for mod in self.allmodules.modules:
            if not hasattr(mod, "commands"):
                logger.debug(f"Modul {mod.__class__.__name__} hali kiritilmagan")
                continue

            if mod.strings["name"] in self.get("hide", []) and not force:
                continue

            tmp = ""

            try:
                name = mod.strings["name"]
            except KeyError:
                name = getattr(mod, "name", "XATO")

            inline = (
                hasattr(mod, "callback_handlers")
                and mod.callback_handlers
                or hasattr(mod, "inline_handlers")
                and mod.inline_handlers
            )

            if not inline:
                for cmd_ in mod.commands.values():
                    try:
                        inline = "await self.inline.form(" in inspect.getsource(
                            cmd_.__code__
                        )
                    except Exception:
                        pass

            core = mod.__origin__ == "<core>"

            if core:
                emoji = self.config["yadro_emoji"]
            elif inline:
                emoji = self.config["shaxsiy_emoji"]
            else:
                emoji = self.config["tekis_emoji"]

            if (
                not getattr(mod, "commands", None)
                and not getattr(mod, "inline_handlers", None)
                and not getattr(mod, "callback_handlers", None)
            ):
                no_commands_ += [
                    self.strings("mod_tmpl").format(self.config["empty_emoji"], name)
                ]
                continue

            tmp += self.strings("mod_tmpl").format(emoji, name)
            first = True

            commands = [
                name
                for name, func in mod.commands.items()
                if await self.allmodules.check_security(message, func) or force
            ]

            for cmd in commands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(cmd)
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(cmd)

            icommands = [
                name
                for name, func in mod.inline_handlers.items()
                if await self.inline.check_inline_security(
                    func=func,
                    user=message.sender_id,
                )
                or force
            ]

            for cmd in icommands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(f"🎹 {cmd}")
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(f"🎹 {cmd}")

            if commands or icommands:
                tmp += " )"
                if core:
                    core_ += [tmp]
                elif inline:
                    inline_ += [tmp]
                else:
                    plain_ += [tmp]
            elif not shown_warn and (mod.commands or mod.inline_handlers):
                reply = (
                    "<i>Faqat bularni bajarishga ruxsatingiz bor"
                    f" commands</i>\n{reply}"
                )
                shown_warn = True

        plain_.sort(key=lambda x: x.split()[1])
        core_.sort(key=lambda x: x.split()[1])
        inline_.sort(key=lambda x: x.split()[1])
        no_commands_.sort(key=lambda x: x.split()[1])
        no_commands_ = "".join(no_commands_) if force else ""

        partial_load = (
            ""
            if self.lookup("Loader")._fully_loaded
            else f"\n\n{self.strings('partial_load')}"
        )

        await utils.answer(
            message,
            f"{reply}\n{''.join(core_)}{''.join(plain_)}{''.join(inline_)}{no_commands_}{partial_load}",
        )

    @loader.command(ru_doc="Показать ссылку на чат помощи Shaxsiy")
    async def support(self, message):
        """Shaxsiy  qo'llab-quvvatlash chati bilan boğlaning"""
        if message.out:
            await self.request_join("@shaxsiy_userbot_guruhi", self.strings("request_join"))

        await utils.answer(
            message,
            self.strings("support").format(
                '<emoji document_id="5192765204898783881">🏕️</emoji><emoji'
                ' document_id="5195311729663286630">☝️</emoji><emoji'
                ' document_id="5195045669324201904">☝️</emoji>'
                if self._client.hikka_me.premium
                else "🔰",
            ),
        )

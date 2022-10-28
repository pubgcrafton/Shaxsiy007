# 🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺
# ⬛⬛⬛🔺🔺🔺⬛⬛🔺🔺⬛🔺🔺🔺⬛🔺⬛⬛⬛🔺⬛🔺🔺🔺⬛🔺🔺⬛⬛🔺🔺⬛⬛⬛🔺🔺
# ⬛🔺🔺⬛🔺⬛🔺🔺⬛🔺⬛⬛🔺🔺⬛🔺🔺⬛🔺🔺⬛🔺🔺🔺⬛🔺⬛🔺🔺⬛🔺⬛🔺🔺⬛🔺
# ⬛🔺🔺⬛🔺⬛🔺🔺⬛🔺⬛🔺⬛🔺⬛🔺🔺⬛🔺🔺🔺⬛🔺⬛🔺🔺⬛🔺🔺⬛🔺⬛⬛⬛🔺🔺
# ⬛🔺🔺⬛🔺⬛🔺🔺⬛🔺⬛🔺🔺⬛⬛🔺🔺⬛🔺🔺🔺🔺⬛🔺🔺🔺⬛🔺🔺⬛🔺⬛🔺🔺⬛🔺
# ⬛⬛⬛🔺🔺🔺⬛⬛🔺🔺⬛🔺🔺🔺⬛🔺⬛⬛⬛🔺🔺🔺⬛🔺🔺🔺🔺⬛⬛🔺🔺⬛🔺🔺🔺⬛
# 🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺
#
#
#                                 © Copyright 2022
#
# https://t.me/DONIYOR_TM | https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html


# scope: inline
# scope: shaxsiy_only
# scope: shaxsiy_min 007

import logging
import git

from telethon.tl.types import Message
from telethon.utils import get_display_name

from .. import loader, main, utils
from ..inline.types import InlineQuery
import datetime
import time

logger = logging.getLogger(__name__)


@loader.tds
class PrivatinfoMod(loader.Module):
    """Show userbot info"""

    strings = {
        "name": "ShaxsiyInfo",
        "owner": "Ega",
        "version": "Versiya",
        "build": "Versiya kodi",
        "prefix": "Prefiks",
        "uptime": "Qayta ishga tushirilgan vaqt",
        "branch": "Filial",
        "up-to-date": "🎡 Ejg oxirgi versiya",
        "update_required": "😕 Yangilanish shart</b><code>.update</code><b>",
        "_cfg_cst_msg": "Ma'lumot uchun maxsus xabar. Mayda bo'lishi mumkin {me}, {version}, {build}, {prefix}, {platform}, {upd}, {time}, {uptime}, {branch} kalit so'zlar",
        "_cfg_cst_btn": "Ma'lumot uchun maxsus tugma. Tugmani olib tashlash uchun bo'sh qoldiring",
        "_cfg_cst_bnr": "Ma'lumot uchun maxsus banner.",
        "_cfg_cst_frmt": "Banner ma'lumotlari uchun maxsus fayl formati.",
        "_cfg_banner": "Rasm bannerini o'chirish uchun True-ni o'rnating",
        "_cfg_time": "server vaqtini to'g'rilash uchun 1, -1, -3 va hokazolardan foydalaning {time}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_message",
                "no",
                doc=lambda: self.strings("_cfg_cst_msg"),
            ),
            loader.ConfigValue(
                "custom_button1",
                ["♻️ admin ♻️", "https://t.me/DONIYOR_TM"],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Series(min_len=0, max_len=2),
            ),
            loader.ConfigValue(
                "custom_button2",
                [],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Series(min_len=0, max_len=2),
            ),
            loader.ConfigValue(
                "custom_button3",
                [],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Series(min_len=0, max_len=2),
            ),
            loader.ConfigValue(
                "custom_banner",
                "https://siasky.net/ZAB5fVs3A0V9MUjzrvFRkwUn8UgN8hu-FecAgWR9GhPSQQ",
                lambda: self.strings("_cfg_cst_bnr"),
            ),
            loader.ConfigValue(
                "disable_banner",
                False,
                lambda: self.strings("_cfg_banner"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_format",
                "photo",
                lambda: self.strings("_cfg_cst_frmt"),
                validator=loader.validators.Choice(["photo", "video", "gif"]),
            ),
            loader.ConfigValue(
                "timezone",  
                "5",
                lambda: self.strings("_cfg_time"),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()

    def _render_info(self) -> str:
        ver = utils.get_git_hash() or "Unknown"

        try:
            repo = git.Repo()
            diff = repo.git.log(["HEAD..origin/master", "--oneline"])
            upd = (
                self.strings("update_required") if diff else self.strings("up-to-date")
            )
        except Exception:
            upd = ""

        me = f'<b><a href="tg://user?id={self._me.id}">{utils.escape_html(get_display_name(self._me))}</a></b>'
        version = f'<i>{".".join(list(map(str, list(main.__version__))))}</i>'
        build = f'<a href="https://github.com/pubgcrafton/shaxsiy/commit/{ver}">#{ver[:8]}</a>'  # fmt: skip
        prefix = f"«<code>{utils.escape_html(self.get_prefix())}</code>»"
        platform = utils.get_named_platform()
        uptime= utils.formatted_uptime()
        offset = datetime.timedelta(hours=self.config["timezone"])
        tz = datetime.timezone(offset)
        time1 = datetime.datetime.now(tz)
        time = time1.strftime("%H:%M:%S")

        return (
            "<b> </b>\n"
            + self.config["custom_message"].format(
                me=me,
                version=version,
                build=build,
                upd=upd,
                prefix=prefix,
                platform=platform,
                uptime=uptime,
                time=time,
            )
            if self.config["custom_message"] != "no"
            else (
                "<b>💢 Shaxsiy Userbot </b>\n"
                f'<b>🧑‍💻 {self.strings("owner")}: </b>{me}\n\n'
                f"<b>🛰 {self.strings('version')}: </b>{version} {build}\n"
                f"<b>{upd}</b>\n"
                f"<b>⏳ Qayta ishga tushirilgan vaqt: {uptime}</b>\n\n"
                f"<b>⌚ Soat: {time}</b>\n"
                f"<b>🎷 {self.strings('prefix')}: </b>{prefix}\n"
                f"<b>📻 Platforma: «{platform}»</b>\n"
                f"<b>🎗 Bu userbot Doniyor Norqulovga tegishli bo'lib ommaviy sanalmaydi!</b>\n"
            )
        )

    def _get_mark(self, int):
        if int == 1:
            return (
                {
                    "text": self.config["custom_button1"][0],
                    "url": self.config["custom_button1"][1],
                }
                if self.config["custom_button1"]
                else None
            )

        elif int == 2:
            return (
                {
                    "text": self.config["custom_button2"][0],
                    "url": self.config["custom_button2"][1],
                }
                if self.config["custom_button2"]
                else None
            )

        elif int == 3:
            return (
                {
                    "text": self.config["custom_button3"][0],
                    "url": self.config["custom_button3"][1],
                }
                if self.config["custom_button3"]
                else None
            )
            
        elif int == 4:
            return (
                {
                    "text": "🔻Yopish",
                    "action": "close",
                }
            )

        elif int == 5:
            return (
                {
                    "text": "🪂Yangilash",
                    "data": "hikka_update",
                }
            )

    @loader.unrestricted
    async def infocmd(self, message: Message):
        """Send userbot info"""
        m1 = self._get_mark(1)
        m2 = self._get_mark(2)
        m3 = self._get_mark(3)
        m4 = self._get_mark(4)
        m5 = self._get_mark(5)

        await self.inline.form(
            message=message,
            text=self._render_info(),
            reply_markup=[
                [
                    *([m1] if m1 else []),
                ],
                [
                    *([m2] if m2 else []),
                    *([m3] if m3 else []),
                ],
                [
                    *([m4] if m4 else []),
                    *([m5] if m5 else []),
                ],
            ],
            **{}
            if self.config["disable_banner"]
            else {self.config["custom_format"]: self.config["custom_banner"]}
        )

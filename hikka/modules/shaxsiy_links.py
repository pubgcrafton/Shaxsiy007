#	████░████░███░███░██░██░████░
#    ░██░░██░░░██░█░██░██░██░███░░
#    ░██░░████░██░░░██░█████░█████
#    ═════════════════════════════════════════
#    ████░████░░██░██░██░███░░██░█████░██░░░██
#    ██░░░███░░░████░░██░██░█░██░██░██░░██░██░
#    ████░█████░██░██░██░██░░███░█████░░░███░░
#    ═════════════════════════════════════════
#    Litsenziya: https://t.me/UModules/112

#▄▀█ █▀▄▀█ █▀█ █▀█ █▀▀
#█▀█ █░▀░█ █▄█ █▀▄ ██▄
#          
#             © Copyright 2022
#
#          https://t.me/the_farkhodov 
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import inspect
from .. import loader, utils, main, security
import logging
import difflib
from telethon.tl.types import Message

__version__ = (1, 0, 0)
# meta developer: @netuzb | modified by @the_farkhodov

@loader.tds
class SearcherMod(loader.Module):
    """Searcher"""

    strings = {
        "name": "shaxsiylinks",
        "yutub": "🫂 <b>You Tube havolasi siz uchun maxsus..</b>\n\n",
        "google": "🫂 <b>Google havolasi siz uchun maxsus.</b>\n\n",
        "github": "🫂 <b>Github havolasi siz uchun maxsus.</b>\n\n",
        "pornhub": "🫂 <b>Pornhub havolasi siz uchun maxsus.</b>\n\n",
    }

    async def ytcmd(self, message):
        """<word> create YouTube link"""
        text = utils.get_args_raw(message) 
        s = f"<b>✏ Kirish so'zi: <code>{text}</code></b>"
        if await self.allmodules.check_security(
            message,
            security.OWNER | security.SUDO,
        ):
            
            try:
                await self.inline.form(
                    self.strings("yutub", message) + s,
                    reply_markup=[                        
                        [{"text": "♨️ Havola", "url": f"https://m.youtube.com/results?sp=mAEA&search_query={text}"}],
                        [{"text": "🔻 Yopish", "action": f"close"}],
                        
                    ],
                    photo="https://i.imgur.com/HhqSKgU.jpeg",
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("join", message))
                

    async def gugcmd(self, message):
        """<word> create Google link"""
        text = utils.get_args_raw(message) 
        s = f"<b>✏ Kirish so'zi: <code>{text}</code></b>"
        if await self.allmodules.check_security(
            message,
            security.OWNER | security.SUDO,
        ):
            
            try:
                await self.inline.form(
                    self.strings("google", message) + s,
                    reply_markup=[
                        [{"text": "♨️ Havola", "url": f"https://www.google.com/search?q={text}"}],
                        [{"text": "🔻 Yopish", "action": f"close"}],
                    ],
                    photo="https://i.imgur.com/OpqRVKk.jpeg",
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("join", message))
                
    async def ghcmd(self, message):
        """<word> create Github link"""
        text = utils.get_args_raw(message) 
        s = f"<b>✏ Kirish so'zi: <code>{text}</code></b>"
        if await self.allmodules.check_security(
            message,
            security.OWNER | security.SUDO,
        ):
            
            try:
                await self.inline.form(
                    self.strings("github", message) + s,
                    reply_markup=[
                        [{"text": "♨️ Havola", "url": f"https://github.com/search?q={text}"}],
                        [{"text": "🔻 Yopish", "action": f"close"}],
                    ],
                    photo="https://i.imgur.com/KgSdnsL.jpeg",
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("join", message))
           
    async def phcmd(self, message):
        """<word> create PornHub link"""
        text = utils.get_args_raw(message) 
        s = f"<b>✏ Kirish so'zi: <code>{text}</code></b>"
        if await self.allmodules.check_security(
            message,
            security.OWNER | security.SUDO,
        ):
            
            try:
                await self.inline.form(
                    self.strings("pornhub", message) + s,
                    reply_markup=[
                        [{"text": "♨️ Havola", "url": f"https://rt.pornhub.com/video/search?search={text}"}],
                        [{"text": "🔻 Yopish", "action": f"close"}],
                    ],
                    photo="https://i.imgur.com/FZPIJtX.jpeg",
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("join", message))
                
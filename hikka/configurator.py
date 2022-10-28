#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2021 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import locale
import os
import string
import sys
import typing

from dialog import Dialog, ExecutableNotFound

from . import utils


def _safe_input(*args, **kwargs):
    """Kirish (*) ni chaqirishga harakat qiling, agar EOFError yoki OSError yuzaga kelsa, xato xabarini chop eting)
    """
    try:
        return input(*args, **kwargs)
    except (EOFError, OSError):
        raise
    except KeyboardInterrupt:
        print()
        return None


class TDialog:
    """Tashqi bog'liqliklarsiz dialog.Dialogni qayta tiklash"""

    def inputbox(self, query: str) -> typing.Tuple[bool, str]:
        """So'rovning matnli kiritilishini oling"""
        print(query)
        print()
        inp = _safe_input("Iltimos, javobingizni kiriting yoki bekor qilish uchun hech narsa yozmang: ")
        return (False, "Cancelled") if not inp else (True, inp)

    def msgbox(self, msg: str) -> bool:
        """Ba'zi ma'lumotlarni chop eting"""
        print(msg)
        return True


TITLE = ""

if sys.stdout.isatty():
    try:
        DIALOG = Dialog(dialog="dialog", autowidgetsize=True)
        locale.setlocale(locale.LC_ALL, "")
    except (ExecutableNotFound, locale.Error):
        # Terminalga asoslangan konfiguratorga qayting.
        DIALOG = TDialog()
else:
    DIALOG = TDialog()


def api_config(data_root: str):
    """Foydalanuvchidan API konfiguratsiyasini so'rang va sozlang"""
    code, hash_value = DIALOG.inputbox("API hashingizni kiriting")
    if code == DIALOG.OK:
        if len(hash_value) != 32 or any(
            it not in string.hexdigits for it in hash_value
        ):
            DIALOG.msgbox("Yaroqsiz hash")
            return

        code, id_value = DIALOG.inputbox("API identifikatoringizni kiriting")

        if not id_value or any(it not in string.digits for it in id_value):
            DIALOG.msgbox("Yaroqsiz ID")
            return

        with open(
            os.path.join(
                data_root or os.path.dirname(utils.get_base_dir()), "api_token.txt"
            ),
            "w",
        ) as file:
            file.write(id_value + "\n" + hash_value)

        DIALOG.msgbox("API tokeni va identifikatori toʻplami.")

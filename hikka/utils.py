"""Utilities"""

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

import asyncio
import functools
import io
import json
import logging
import os
import random
import re
import shlex
import string
import time
import inspect
from datetime import timedelta
from typing import Any, List, Optional, Tuple, Union
from urllib.parse import urlparse

import git
import grapheme
import requests
import telethon
from telethon.hints import Entity
from telethon.tl.custom.message import Message
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from telethon.tl.functions.messages import (
    GetDialogFiltersRequest,
    UpdateDialogFilterRequest,
    SetHistoryTTLRequest,
)
from telethon.tl.types import (
    Channel,
    InputPeerNotifySettings,
    MessageEntityBankCard,
    MessageEntityBlockquote,
    MessageEntityBold,
    MessageEntityBotCommand,
    MessageEntityCashtag,
    MessageEntityCode,
    MessageEntityEmail,
    MessageEntityHashtag,
    MessageEntityItalic,
    MessageEntityMention,
    MessageEntityMentionName,
    MessageEntityPhone,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityUnknown,
    MessageEntityUrl,
    MessageMediaWebPage,
    PeerChannel,
    PeerChat,
    PeerUser,
    User,
    Chat,
    UpdateNewChannelMessage,
)

from aiogram.types import Message as AiogramMessage

from .inline.types import InlineCall, InlineMessage
from .types import Module
from .tl_cache import CustomTelegramClient


FormattingEntity = Union[
    MessageEntityUnknown,
    MessageEntityMention,
    MessageEntityHashtag,
    MessageEntityBotCommand,
    MessageEntityUrl,
    MessageEntityEmail,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityCode,
    MessageEntityPre,
    MessageEntityTextUrl,
    MessageEntityMentionName,
    MessageEntityPhone,
    MessageEntityCashtag,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntityBlockquote,
    MessageEntityBankCard,
    MessageEntitySpoiler,
]

ListLike = Union[list, set, tuple]

emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)

parser = telethon.utils.sanitize_parse_mode("html")


def get_args(message: Message) -> List[str]:
    """( str yoki Xabar ) xabaridan dalillarni oling, dalillar ro'yxatini qaytaring"""
    if not (message := getattr(message, "message", message)):
        return False

    if len(message := message.split(maxsplit=1)) <= 1:
        return []

    message = message[1]

    try:
        split = shlex.split(message)
    except ValueError:
        return message  # Cannot split, let's assume that it's just one long message

    return list(filter(lambda x: len(x) > 0, split))


def get_args_raw(message: Message) -> str:
    """( split emas ) xom satr sifatida buyruqqa parametrlarni oling"""
    if not (message := getattr(message, "message", message)):
        return False

    return args[1] if len(args := message.split(maxsplit=1)) > 1 else ""


def get_args_split_by(message: Message, separator: str) -> List[str]:
    """Arglarni ma'lum bir ajratgich bilan ajrating"""
    return [
        section.strip() for section in get_args_raw(message).split(separator) if section
    ]


def get_chat_id(message: Union[Message, AiogramMessage]) -> int:
    """Chat identifikatorini oling, lekin agar kanal bo'lsa -100 bo'lmaydi"""
    return telethon.utils.resolve_id(
        getattr(message, "chat_id", None)
        or getattr(getattr(message, "chat", None), "id", None)
    )[0]


def get_entity_id(entity: Entity) -> int:
    """ID-shaxs olish"""
    return telethon.utils.get_peer_id(entity)


def escape_html(text: str, /) -> str:  # sourcery skip
    """Barcha ishonchsiz / potentsial buzilgan ma'lumotlarni bu erga o'tkazing"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_quotes(text: str, /) -> str:
    """Qo'shtirnoqlarni html tirnoqlariga qo'shib qo'ying"""
    return escape_html(text).replace('"', "&quot;")


def get_base_dir() -> str:
    """Ushbu fayl katalogini oling"""
    from . import __main__

    return get_dir(__main__.__file__)


def get_dir(mod: str) -> str:
    """Berilgan modul katalogini oling"""
    return os.path.abspath(os.path.dirname(os.path.abspath(mod)))


async def get_user(message: Message) -> Union[None, User]:
    """Xabar yuborgan foydalanuvchini qidirib toping, agar topilmasa"""
    try:
        return await message.client.get_entity(message.sender_id)
    except ValueError:  # Not in database. Lets go looking for them.
        logging.debug("Foydalanuvchi sessiya keshida emas. Qidirmoqda...")

    if isinstance(message.peer_id, PeerUser):
        await message.client.get_dialogs()
        return await message.client.get_entity(message.sender_id)

    if isinstance(message.peer_id, (PeerChannel, PeerChat)):
        try:
            return await message.client.get_entity(message.sender_id)
        except Exception:
            pass

        async for user in message.client.iter_participants(
            message.peer_id,
            aggressive=True,
        ):
            if user.id == message.sender_id:
                return user

        logging.error("Foydalanuvchi ular xabar yuborgan guruhda yo'q")
        return None

    logging.error("`peer_id` foydalanuvchi, suhbat yoki kanal emas")
    return None


def run_sync(func, *args, **kwargs):
    """
    Sinxron bo'lmagan funktsiyani yangi ipga ishga tushiring va kutilgan narsani qaytaring
    :param func: Bajarish uchun faqat sinxronlash funktsiyasi
    :qaytish: Kutilayotgan korutin
    """
    return asyncio.get_event_loop().run_in_executor(
        None,
        functools.partial(func, *args, **kwargs),
    )


def run_async(loop, coro):
    """Async funktsiyasini asenksiz funktsiya sifatida ishga tushiring, uni tugaguncha blokirovka qiling"""
    # When we bump minimum support to 3.7, use run()
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


def censor(
    obj,
    to_censor: Optional[List[str]] = None,
    replace_with: str = "redacted_{count}_chars",
):
    """Asl ob'ektni o'zgartirishi mumkin, ammo unga ishonmang"""
    if to_censor is None:
        to_censor = ["phone"]

    for k, v in vars(obj).items():
        if k in to_censor:
            setattr(obj, k, replace_with.format(count=len(v)))
        elif k[0] != "_" and hasattr(v, "__dict__"):
            setattr(obj, k, censor(v, to_censor, replace_with))

    return obj


def relocate_entities(
    entities: list,
    offset: int,
    text: Optional[str] = None,
) -> list:
    """Barcha ob'ektlarni ofset orqali siljiting ( ) matnida"""
    length = len(text) if text is not None else 0

    for ent in entities.copy() if entities else ():
        ent.offset += offset
        if ent.offset < 0:
            ent.length += ent.offset
            ent.offset = 0
        if text is not None and ent.offset + ent.length > length:
            ent.length = length - ent.offset
        if ent.length <= 0:
            entities.remove(ent)

    return entities


async def answer(
    message: Union[Message, InlineCall, InlineMessage],
    response: str,
    *,
    reply_markup: Optional[Union[List[List[dict]], List[dict], dict]] = None,
    **kwargs,
) -> Union[InlineCall, InlineMessage, Message]:
    """Bu buyruqqa javob berish uchun foydalaning"""
    # Compatibility with FTG\GeekTG

    if isinstance(message, list) and message:
        message = message[0]

    if reply_markup is not None:
        if not isinstance(reply_markup, (list, dict)):
            raise ValueError("reply_markup must be a list or dict")

        if reply_markup:
            if isinstance(message, (InlineMessage, InlineCall)):
                await message.edit(response, reply_markup)
                return

            reply_markup = message.client.loader.inline._normalize_markup(reply_markup)
            result = await message.client.loader.inline.form(
                response,
                message=message if message.out else get_chat_id(message),
                reply_markup=reply_markup,
                **kwargs,
            )
            return result

    if isinstance(message, (InlineMessage, InlineCall)):
        await message.edit(response)
        return message

    kwargs.setdefault("link_preview", False)

    if not (edit := (message.out and not message.via_bot_id and not message.fwd_from)):
        kwargs.setdefault(
            "reply_to",
            getattr(message, "reply_to_msg_id", None),
        )

    parse_mode = telethon.utils.sanitize_parse_mode(
        kwargs.pop(
            "parse_mode",
            message.client.parse_mode,
        )
    )

    if isinstance(response, str) and not kwargs.pop("asfile", False):
        text, entities = parse_mode.parse(response)

        if len(text) >= 4096 and not hasattr(message, "hikka_grepped"):
            try:
                if not message.client.loader.inline.init_complete:
                    raise

                strings = list(smart_split(text, entities, 4096))

                if len(strings) > 10:
                    raise

                list_ = await message.client.loader.inline.list(
                    message=message,
                    strings=strings,
                )

                if not list_:
                    raise

                return list_
            except Exception:
                file = io.BytesIO(text.encode("utf-8"))
                file.name = "command_result.txt"

                result = await message.client.send_file(
                    message.peer_id,
                    file,
                    caption=(
                        "<b>📤 Buyruq chiqishi juda uzoq bo'lib tuyuladi, shuning uchun u yuborildi"
                        " file.</b>"
                    ),
                )

                if message.out:
                    await message.delete()

                return result

        result = await (message.edit if edit else message.respond)(
            text,
            parse_mode=lambda t: (t, entities),
            **kwargs,
        )
    elif isinstance(response, Message):
        if message.media is None and (
            response.media is None or isinstance(response.media, MessageMediaWebPage)
        ):
            result = await message.edit(
                response.message,
                parse_mode=lambda t: (t, response.entities or []),
                link_preview=isinstance(response.media, MessageMediaWebPage),
            )
        else:
            result = await message.respond(response, **kwargs)
    else:
        if isinstance(response, bytes):
            response = io.BytesIO(response)
        elif isinstance(response, str):
            response = io.BytesIO(response.encode("utf-8"))

        if name := kwargs.pop("filename", None):
            response.name = name

        if message.media is not None and edit:
            await message.edit(file=response, **kwargs)
        else:
            kwargs.setdefault(
                "reply_to",
                getattr(message, "reply_to_msg_id", None),
            )
            result = await message.client.send_file(message.peer_id, response, **kwargs)
            if message.out:
                await message.delete()

    return result


async def get_target(message: Message, arg_no: int = 0) -> Union[int, None]:
    if any(
        isinstance(entity, MessageEntityMentionName)
        for entity in (message.entities or [])
    ):
        e = sorted(
            filter(lambda x: isinstance(x, MessageEntityMentionName), message.entities),
            key=lambda x: x.offset,
        )[0]
        return e.user_id

    if len(get_args(message)) > arg_no:
        user = get_args(message)[arg_no]
    elif message.is_reply:
        return (await message.get_reply_message()).sender_id
    elif hasattr(message.peer_id, "user_id"):
        user = message.peer_id.user_id
    else:
        return None

    try:
        entity = await message.client.get_entity(user)
    except ValueError:
        return None
    else:
        if isinstance(entity, User):
            return entity.id


def merge(a: dict, b: dict) -> dict:
    """Lug'at a lug'at bilan almashtirish b"""
    for key in a:
        if key in b:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                b[key] = merge(a[key], b[key])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                b[key] = list(set(b[key] + a[key]))
            else:
                b[key] = a[key]

        b[key] = a[key]

    return b


async def set_avatar(
    client: CustomTelegramClient,
    peer: Entity,
    avatar: str,
) -> bool:
    """Korxona avatarini o'rnatadi"""
    if isinstance(avatar, str) and check_url(avatar):
        f = (
            await run_sync(
                requests.get,
                avatar,
            )
        ).content
    elif isinstance(avatar, bytes):
        f = avatar
    else:
        return False

    res = await client(
        EditPhotoRequest(
            channel=peer,
            photo=await client.upload_file(f, file_name="photo.png"),
        )
    )

    try:
        await client.delete_messages(
            peer,
            message_ids=[
                next(
                    update
                    for update in res.updates
                    if isinstance(update, UpdateNewChannelMessage)
                ).message.id
            ],
        )
    except Exception:
        pass

    return True


async def asset_channel(
    client: CustomTelegramClient,
    title: str,
    description: str,
    *,
    channel: bool = False,
    silent: bool = False,
    archive: bool = False,
    avatar: Optional[str] = None,
    ttl: Optional[int] = None,
    _folder: Optional[str] = None,
) -> Tuple[Channel, bool]:
    """
    Agar kerak bo'lsa, ( yangi kanalini yarating va o'z tashkilotini qaytaring
    :param mijoz: Telegram mijozi tomonidan kanal yaratish uchun
    :param sarlavhasi: Kanal nomi
    :param tavsifi: Ta'rif
    :param kanali: Kanal yoki supergrup yaratish kerakmi
    :param jim: Avtomatik ravishda kanalni o'chirish
    :param arxivi: Avtomatik arxiv kanali
    :param avatar: Url-dan avatarga yaratilgan tengdoshning pfp-si sifatida
    :param ttl: Kanaldagi xabarlar uchun yashash vaqti
    :param _folder: Uni ishlatmang, aks holda narsalar yomonlashadi
    :qaytish: Peer va bool: yangi yoki oldindan mavjud
    """
    if not hasattr(client, "_channels_cache"):
        client._channels_cache = {}

    if (
        title in client._channels_cache
        and client._channels_cache[title]["exp"] > time.time()
    ):
        return client._channels_cache[title]["peer"], False

    async for d in client.iter_dialogs():
        if d.title == title:
            client._channels_cache[title] = {"peer": d.entity, "exp": int(time.time())}
            return d.entity, False

    peer = (
        await client(
            CreateChannelRequest(
                title,
                description,
                megagroup=not channel,
            )
        )
    ).chats[0]

    if silent:
        await dnd(client, peer, archive)
    elif archive:
        await client.edit_folder(peer, 1)

    if avatar:
        await set_avatar(client, peer, avatar)

    if ttl:
        await client(SetHistoryTTLRequest(peer=peer, period=ttl))

    if _folder:
        if _folder != "shaxsiy":
            raise NotImplementedError

        folders = await client(GetDialogFiltersRequest())

        try:
            folder = next(folder for folder in folders if folder.title == "shaxsiy")
        except Exception:
            folder = None

        if folder is not None and not any(
            peer.id == getattr(folder_peer, "channel_id", None)
            for folder_peer in folder.include_peers
        ):
            folder.include_peers += [await client.get_input_entity(peer)]

            await client(
                UpdateDialogFilterRequest(
                    folder.id,
                    folder,
                )
            )

    client._channels_cache[title] = {"peer": peer, "exp": int(time.time())}
    return peer, True


async def dnd(
    client: CustomTelegramClient,
    peer: Entity,
    archive: bool = True,
) -> bool:
    """
    Ovozlar va ixtiyoriy ravishda arxivlar tengdoshi
    :param peer: har qanday narsaga bog'liqlik
    :param arxivi: Arxiv tengdoshi yoki shunchaki soqovmi?
    :qaytadi: Muvaffaqiyatga to'g'ri keladi, aks holda noto'g'ri
    """
    try:
        await client(
            UpdateNotifySettingsRequest(
                peer=peer,
                settings=InputPeerNotifySettings(
                    show_previews=False,
                    silent=True,
                    mute_until=2**31 - 1,
                ),
            )
        )

        if archive:
            await client.edit_folder(peer, 1)
    except Exception:
        logging.exception("utils.dnd error")
        return False

    return True


def get_link(user: Union[User, Channel], /) -> str:
    """Telegrammani doimiy ravishda olish"""
    return (
        f"tg://user?id={user.id}"
        if isinstance(user, User)
        else (
            f"tg://resolve?domain={user.username}"
            if getattr(user, "username", None)
            else ""
        )
    )


def chunks(_list: Union[list, tuple, set], n: int, /) -> list:
    """_ Ro'yxatni 'n' bo'laklariga bo'lish"""
    return [_list[i : i + n] for i in range(0, len(_list), n)]


def get_named_platform() -> str:
    """Formatlangan platforma nomini qaytaradi"""
    try:
        if os.path.isfile("/proc/device-tree/model"):
            with open("/proc/device-tree/model") as f:
                model = f.read()
                if "Orange" in model:
                    return f"🍊 {model}"

                return f"🍇 {model}" if "Raspberry" in model else f"❓ {model}"
    except Exception:
        # In case of weird fs, aka Termux
        pass

    try:
        from platform import uname

        if "microsoft-standard" in uname().release:
            return "🍁 WSL"
    except Exception:
        pass

    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    is_okteto = "OKTETO" in os.environ
    is_railway = "RAILWAY" in os.environ
    is_docker = "DOCKER" in os.environ
    is_heroku = "DYNO" in os.environ
    is_codespaces = "CODESPACES" in os.environ

    if is_heroku:
        return "♓️ Heroku"

    if is_railway:
        return "🚂 Railway"

    if is_docker:
        return "🐳 Docker"

    if is_termux:
        return "🕶 Termux"

    if is_okteto:
        return "☁️ Okteto"

    if is_codespaces:
        return "🐈‍⬛ Codespaces"

    is_lavhost = "LAVHOST" in os.environ
    return f"✌️ lavHost {os.environ['LAVHOST']}" if is_lavhost else "📻 VDS"


def get_platform_emoji() -> str:
    BASE = (
        "<emoji document_id={}>💢</emoji><emoji"
        " document_id=5195311729663286630>💢</emoji><emoji"
        " document_id=5195045669324201904>💢</emoji>"
    )

    if "OKTETO" in os.environ:
        return BASE.format(5192767786174128165)

    if "CODESPACES" in os.environ:
        return BASE.format(5194976881127989720)

    if "DYNO" in os.environ:
        return BASE.format(5192845434887873156)

    if "com.termux" in os.environ.get("PREFIX", ""):
        return BASE.format(5193051778001673828)

    if "RAILWAY" in os.environ:
        return BASE.format(5199607521593007466)

    return BASE.format(5192765204898783881)


def uptime() -> int:
    """Bir necha soniya ichida userbot to'planishini qaytaradi"""
    return round(time.perf_counter() - init_ts)


def formatted_uptime() -> str:
    """Formalangan ish vaqtini qaytaradi"""
    return f"{str(timedelta(seconds=uptime()))}"


def ascii_face() -> str:
    """Yoqimli ASCII-art yuzini qaytaradi"""
    return escape_html(
        random.choice(
            [
                "ヽ(๑◠ܫ◠๑)ﾉ",
                "(◕ᴥ◕ʋ)",
                "ᕙ(`▽´)ᕗ",
                "(✿◠‿◠)",
                "(▰˘◡˘▰)",
                "(˵ ͡° ͜ʖ ͡°˵)",
                "ʕっ•ᴥ•ʔっ",
                "( ͡° ᴥ ͡°)",
                "(๑•́ ヮ •̀๑)",
                "٩(^‿^)۶",
                "(っˆڡˆς)",
                "ψ(｀∇´)ψ",
                "⊙ω⊙",
                "٩(^ᴗ^)۶",
                "(´・ω・)っ由",
                "( ͡~ ͜ʖ ͡°)",
                "✧♡(◕‿◕✿)",
                "โ๏௰๏ใ ื",
                "∩｡• ᵕ •｡∩ ♡",
                "(♡´౪`♡)",
                "(◍＞◡＜◍)⋈。✧♡",
                "╰(✿´⌣`✿)╯♡",
                "ʕ•ᴥ•ʔ",
                "ᶘ ◕ᴥ◕ᶅ",
                "▼・ᴥ・▼",
                "ฅ^•ﻌ•^ฅ",
                "(΄◞ิ౪◟ิ‵)",
                "٩(^ᴗ^)۶",
                "ᕴｰᴥｰᕵ",
                "ʕ￫ᴥ￩ʔ",
                "ʕᵕᴥᵕʔ",
                "ʕᵒᴥᵒʔ",
                "ᵔᴥᵔ",
                "(✿╹◡╹)",
                "(๑￫ܫ￩)",
                "ʕ·ᴥ·　ʔ",
                "(ﾉ≧ڡ≦)",
                "(≖ᴗ≖✿)",
                "（〜^∇^ )〜",
                "( ﾉ･ｪ･ )ﾉ",
                "~( ˘▾˘~)",
                "(〜^∇^)〜",
                "ヽ(^ᴗ^ヽ)",
                "(´･ω･`)",
                "₍ᐢ•ﻌ•ᐢ₎*･ﾟ｡",
                "(。・・)_且",
                "(=｀ω´=)",
                "(*•‿•*)",
                "(*ﾟ∀ﾟ*)",
                "(☉⋆‿⋆☉)",
                "ɷ◡ɷ",
                "ʘ‿ʘ",
                "(。-ω-)ﾉ",
                "( ･ω･)ﾉ",
                "(=ﾟωﾟ)ﾉ",
                "(・ε・`*) …",
                "ʕっ•ᴥ•ʔっ",
                "(*˘︶˘*)",
            ]
        )
    )


def array_sum(array: List[Any], /) -> List[Any]:
    """Asosiy summani ketma-ket bajariladi"""
    result = []
    for item in array:
        result += item

    return result


def rand(size: int, /) -> str:
    """Len `size` tasodifiy qatorini qaytaring"""
    return "".join(
        [random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for _ in range(size)]
    )


def smart_split(
    text: str,
    entities: List[FormattingEntity],
    length: int = 4096,
    split_on: ListLike = ("\n", " "),
    min_length: int = 1,
):
    """
    Xabarni kichikroq xabarlarga ajrating.
    Grafika hech qachon buzilmaydi. Korxonalar kerakli joyga mos ravishda ko'chiriladi. Hech qanday kirish mutatsiyaga uchramaydi.
    Har bir xabarning oxiri, oxirgisidan tashqari, [ split_on ] belgilaridan mahrum qilingan
    :param matni: oddiy matn kiritish
    :param sub'ektlari: sub'ektlar
    :param uzunligi: bitta xabarning maksimal uzunligi
    :param split_on: xabarlarni buzish uchun afzal bo'lgan ( yoki satrlar ) belgilari
    :param min_length: har bir xabarga ushbu belgilar sonidan oldin [ split_on ] satrlaridagi har qanday mosliklarga e'tibor bermang
    :qaytish:
    """

    # Authored by @bsolute
    # https://t.me/LonamiWebs/27777

    encoded = text.encode("utf-16le")
    pending_entities = entities
    text_offset = 0
    bytes_offset = 0
    text_length = len(text)
    bytes_length = len(encoded)

    while text_offset < text_length:
        if bytes_offset + length * 2 >= bytes_length:
            yield parser.unparse(
                text[text_offset:],
                list(sorted(pending_entities, key=lambda x: x.offset)),
            )
            break

        codepoint_count = len(
            encoded[bytes_offset : bytes_offset + length * 2].decode(
                "utf-16le",
                errors="ignore",
            )
        )

        for search in split_on:
            search_index = text.rfind(
                search,
                text_offset + min_length,
                text_offset + codepoint_count,
            )
            if search_index != -1:
                break
        else:
            search_index = text_offset + codepoint_count

        split_index = grapheme.safe_split_index(text, search_index)

        split_offset_utf16 = (
            len(text[text_offset:split_index].encode("utf-16le"))
        ) // 2
        exclude = 0

        while (
            split_index + exclude < text_length
            and text[split_index + exclude] in split_on
        ):
            exclude += 1

        current_entities = []
        entities = pending_entities.copy()
        pending_entities = []

        for entity in entities:
            if (
                entity.offset < split_offset_utf16
                and entity.offset + entity.length > split_offset_utf16 + exclude
            ):
                # spans boundary
                current_entities.append(
                    _copy_tl(
                        entity,
                        length=split_offset_utf16 - entity.offset,
                    )
                )
                pending_entities.append(
                    _copy_tl(
                        entity,
                        offset=0,
                        length=entity.offset
                        + entity.length
                        - split_offset_utf16
                        - exclude,
                    )
                )
            elif entity.offset < split_offset_utf16 < entity.offset + entity.length:
                # overlaps boundary
                current_entities.append(
                    _copy_tl(
                        entity,
                        length=split_offset_utf16 - entity.offset,
                    )
                )
            elif entity.offset < split_offset_utf16:
                # wholly left
                current_entities.append(entity)
            elif (
                entity.offset + entity.length
                > split_offset_utf16 + exclude
                > entity.offset
            ):
                # overlaps right boundary
                pending_entities.append(
                    _copy_tl(
                        entity,
                        offset=0,
                        length=entity.offset
                        + entity.length
                        - split_offset_utf16
                        - exclude,
                    )
                )
            elif entity.offset + entity.length > split_offset_utf16 + exclude:
                # wholly right
                pending_entities.append(
                    _copy_tl(
                        entity,
                        offset=entity.offset - split_offset_utf16 - exclude,
                    )
                )

        current_text = text[text_offset:split_index]
        yield parser.unparse(
            current_text,
            list(sorted(current_entities, key=lambda x: x.offset)),
        )

        text_offset = split_index + exclude
        bytes_offset += len(current_text.encode("utf-16le"))


def _copy_tl(o, **kwargs):
    d = o.to_dict()
    del d["_"]
    d.update(kwargs)
    return o.__class__(**d)


def check_url(url: str) -> bool:
    """URL-ning haqiqiyligini tekshiradi"""
    try:
        return bool(urlparse(url).netloc)
    except Exception:
        return False


def get_git_hash() -> Union[str, bool]:
    """Hozirgi shaxsiy git hash oling"""
    try:
        repo = git.Repo()
        return repo.heads[0].commit.hexsha
    except Exception:
        return False


def get_commit_url() -> str:
    """Hozirgi shaxsiy userbot git url qiling"""
    try:
        repo = git.Repo()
        hash_ = repo.heads[0].commit.hexsha
        return (
            f'<a href="https://github.com/pubgcrafton/shaxsiy/commit/{hash_}">#{hash_[:7]}</a>'
        )
    except Exception:
        return "Unknown"


def is_serializable(x: Any, /) -> bool:
    """Ob'ekt JSON-seriyali bo'lishi mumkinligini tekshirish"""
    try:
        json.dumps(x)
        return True
    except Exception:
        return False


def get_lang_flag(countrycode: str) -> str:
    """
    Belgilangan mamlakat kodining emoji oladi
    :param mamlakat kodi: 2 harfli mamlakat kodi
    :qaytish: Emoji bayrog'i
    """
    if (
        len(
            code := [
                c
                for c in countrycode.lower()
                if c in string.ascii_letters + string.digits
            ]
        )
        == 2
    ):
        return "".join([chr(ord(c.upper()) + (ord("🇦") - ord("A"))) for c in code])

    return countrycode


def get_entity_url(
    entity: Union[User, Channel],
    openmessage: bool = False,
) -> str:
    """
    Agar mavjud bo'lsa, ob'ektga havolani oling
    :param ob'ekti: url olish uchun shaxs
    :param ochiq xabar: foydalanuvchilar uchun tg: // openmessage havolasidan foydalaning
    :qaytish: Ob'ektga yoki bo'sh satrga bog'lanish
    """
    return (
        (
            f"tg://openmessage?id={entity.id}"
            if openmessage
            else f"tg://user?id={entity.id}"
        )
        if isinstance(entity, User)
        else (
            f"tg://resolve?domain={entity.username}"
            if getattr(entity, "username", None)
            else ""
        )
    )


async def get_message_link(
    message: Message,
    chat: Optional[Union[Chat, Channel]] = None,
) -> str:
    if message.is_private:
        return (
            f"tg://openmessage?user_id={get_chat_id(message)}&message_id={message.id}"
        )

    if not chat:
        chat = await message.get_chat()

    return (
        f"https://t.me/{chat.username}/{message.id}"
        if getattr(chat, "username", False)
        else f"https://t.me/c/{chat.id}/{message.id}"
    )


def remove_html(text: str, escape: bool = False, keep_emojis: bool = False) -> str:
    """
    HTML teglarini matndan o'chirib tashlaydi
    :param matni: HTML-ni o'chirish uchun matn
    :param qochish: HTMLdan qoching
    :param colp_emojis: odatiy emojisni saqlang
    :qaytish: HTMLsiz matn
    """
    return (escape_html if escape else str)(
        re.sub(
            r"(<\/?a.*?>|<\/?b>|<\/?i>|<\/?u>|<\/?strong>|<\/?em>|<\/?code>|<\/?strike>|<\/?del>|<\/?pre.*?>)"
            if keep_emojis
            else r"(<\/?a.*?>|<\/?b>|<\/?i>|<\/?u>|<\/?strong>|<\/?em>|<\/?code>|<\/?strike>|<\/?del>|<\/?pre.*?>|<\/?emoji.*?>)",
            "",
            text,
        )
    )


def get_kwargs() -> dict:
    """
    Kvarg funktsiyasini oling, bunda deyiladi
    :qaytish: kwargs
    """
    # https://stackoverflow.com/a/65927265/19170642
    frame = inspect.currentframe().f_back
    keys, _, _, values = inspect.getargvalues(frame)
    return {key: values[key] for key in keys if key != "self"}


def mime_type(message: Message) -> str:
    """
    Xabarda mime turdagi hujjatni oling
    :param xabari: Hujjat bilan xabar
    :orqaga qaytish: Mime turi yoki bo'sh satr, agar mavjud bo'lmasa
    """
    return (
        ""
        if not isinstance(message, Message) or not getattr(message, "media", False)
        else getattr(getattr(message, "media", False), "mime_type", False) or ""
    )


def find_caller(stack: Optional[List[inspect.FrameInfo]] = None) -> Any:
    """Stack-da buyruq topishga urinishlar"""
    caller = next(
        (
            frame_info
            for frame_info in stack or inspect.stack()
            if hasattr(frame_info, "function")
            and any(
                inspect.isclass(cls_)
                and issubclass(cls_, Module)
                and cls_ is not Module
                for cls_ in frame_info.frame.f_globals.values()
            )
        ),
        None,
    )

    if not caller:
        return next(
            (
                frame_info.frame.f_locals["func"]
                for frame_info in stack or inspect.stack()
                if hasattr(frame_info, "function")
                and frame_info.function == "future_dispatcher"
                and (
                    "CommandDispatcher"
                    in getattr(getattr(frame_info, "frame", None), "f_globals", {})
                )
            ),
            None,
        )

    return next(
        (
            getattr(cls_, caller.function, None)
            for cls_ in caller.frame.f_globals.values()
            if inspect.isclass(cls_) and issubclass(cls_, Module)
        ),
        None,
    )


def validate_html(html: str) -> str:
    """Buzilgan teglarni html-dan olib tashlaydi"""
    text, entities = telethon.extensions.html.parse(html)
    return telethon.extensions.html.unparse(escape_html(text), entities)


init_ts = time.perf_counter()


# GeekTG Compatibility
def get_git_info():
    # https://github.com/GeekTG/Friendly-Telegram/blob/master/friendly-telegram/utils.py#L133
    try:
        repo = git.Repo()
        ver = repo.heads[0].commit.hexsha
    except Exception:
        ver = ""

    return [
        ver,
        f"https://github.com/pubgcrafton/shaxsiy/commit/{ver}" if ver else "",
    ]


def get_version_raw():
    """Userbot versiyasini oling"""
    # https://github.com/GeekTG/Friendly-Telegram/blob/master/friendly-telegram/utils.py#L128
    from . import version

    return ".".join(list(map(str, list(version.__version__))))


get_platform_name = get_named_platform

import asyncio
import os
import random
import shutil
import time
import platform
import sys
from random import randint
from telethon import __version__ as tver
from pyrogram import __version__ as pver
from platform import python_version
from pytgcalls import __version__ as pyt
from xteam.version import ultroid_version as UltVer
from xteam.version import __version__ as xtver
from xteam.configs import Var
from . import HOSTED_ON

try:
    from pytz import timezone
except ImportError:
    timezone = None

from telethon.errors import (
    ChannelsTooMuchError,
    ChatAdminRequiredError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserNotParticipantError,
)
from telethon.tl.custom import Button
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import (
    ChatAdminRights,
    ChatPhotoEmpty,
    InputChatUploadedPhoto,
    InputMessagesFilterDocument,
)
from telethon.utils import get_peer_id
from decouple import config, RepositoryEnv
from .. import LOGS, ULTConfig
from ..fns.helper import download_file, inline_mention, updater

db_url = 0
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

async def autoupdate_local_database():
    from .. import asst, udB, ultroid_bot
    global db_url
    db_url = udB.get_key("TGDB_URL") or Var.TGDB_URL or ultroid_bot._cache.get("TGDB_URL")
    if db_url:
        _split = db_url.split("/")
        _channel = _split[-2]
        _id = _split[-1]
        try:
            await asst.edit_message(
                int(_channel) if _channel.isdigit() else _channel,
                message=_id,
                file="database.json",
                text="**Do not delete this file.**",
            )
        except MessageNotModifiedError: return
        except MessageIdInvalidError: pass
    try:
        LOG_CHANNEL = udB.get_key("LOG_CHANNEL") or Var.LOG_CHANNEL or asst._cache.get("LOG_CHANNEL") or "me"
        msg = await asst.send_message(LOG_CHANNEL, "**Do not delete this file.**", file="database.json")
        asst._cache["TGDB_URL"] = msg.message_link
        udB.set_key("TGDB_URL", msg.message_link)
    except Exception as ex:
        LOGS.error(f"Error on autoupdate_local_database: {ex}")

def update_envs():
    from .. import udB
    _envs = [*list(os.environ)]
    if ".env" in os.listdir("."):
        [_envs.append(_) for _ in list(RepositoryEnv(config._find_file(".")).data)]
    for envs in _envs:
        if envs in ["LOG_CHANNEL", "BOT_TOKEN", "BOTMODE", "DUAL_MODE", "language"] or envs in udB.keys():
            if _value := os.environ.get(envs):
                udB.set_key(envs, _value)
            else:
                udB.set_key(envs, config.config.get(envs))

async def startup_stuff():
    from .. import udB
    folders = ["resources/auth", "resources/downloads", "resources/extras"]
    for f in folders:
        f_path = os.path.join(BASE_PATH, f)
        if not os.path.isdir(f_path):
            os.makedirs(f_path, exist_ok=True)
    CT = udB.get_key("CUSTOM_THUMBNAIL")
    if CT:
        path = os.path.join(BASE_PATH, "resources/extras/thumbnail.jpg")
        ULTConfig.thumb = path
        try: await download_file(CT, path)
        except Exception as er: LOGS.exception(er)
    elif CT is False:
        ULTConfig.thumb = None
    GT = udB.get_key("GDRIVE_AUTH_TOKEN")
    if GT:
        with open(os.path.join(BASE_PATH, "resources/auth/gdrive_creds.json"), "w") as t_file:
            t_file.write(GT)
    MM, MP = udB.get_key("MEGA_MAIL"), udB.get_key("MEGA_PASS")
    if MM and MP:
        with open(".megarc", "w") as mega:
            mega.write(f"[Login]\nUsername = {MM}\nPassword = {MP}")
    TZ = udB.get_key("TIMEZONE")
    if TZ and timezone:
        try:
            timezone(TZ)
            os.environ["TZ"] = TZ
            time.tzset()
        except Exception:
            os.environ["TZ"] = "UTC"
            time.tzset()

async def autobot():
    from .. import udB, ultroid_bot
    if udB.get_key("BOT_TOKEN"): return
    await ultroid_bot.start()
    who = ultroid_bot.me
    name = who.first_name + "Bot"
    username = (who.username + "_bot") if who.username else f"xteam_{str(who.id)[5:]}_bot"
    bf = "@BotFather"
    await ultroid_bot(UnblockRequest(bf))
    await ultroid_bot.send_message(bf, "/cancel")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "/newbot")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, name)
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, username)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("Done!"):
        token = isdone.split("`")[1]
        udB.set_key("BOT_TOKEN", token)
        await enable_inline(ultroid_bot, username)
    else: sys.exit(1)

async def autopilot():
    from .. import asst, udB, ultroid_bot
    channel = udB.get_key("LOG_CHANNEL")
    if channel:
        try: chat = await ultroid_bot.get_entity(channel)
        except Exception:
            udB.del_key("LOG_CHANNEL")
            channel = None
    if not channel:
        r = await ultroid_bot(CreateChannelRequest(title="My Userbot Logs", megagroup=True))
        chat = r.chats[0]
        channel = get_peer_id(chat)
        udB.set_key("LOG_CHANNEL", channel)
    try: await ultroid_bot(InviteToChannelRequest(int(channel), [asst.me.username]))
    except Exception: pass

async def customize():
    from .. import asst, udB, ultroid_bot
    try:
        if asst.me.photo: return
        UL = f"@{asst.me.username}"
        file = os.path.join(BASE_PATH, "resources/extras/profile.jpg")
        if not os.path.exists(file):
            file, _ = await download_file("https://files.catbox.moe/k9ljse.jpg", file)
        await ultroid_bot.send_message("botfather", "/setuserpic")
        await asyncio.sleep(1)
        await ultroid_bot.send_message("botfather", UL)
        await asyncio.sleep(1)
        await ultroid_bot.send_file("botfather", file)
    except Exception as e: LOGS.exception(e)

async def plug(plugin_channels):
    from .. import ultroid_bot
    from .utils import load_addons
    addons_path = os.path.join(BASE_PATH, "addons")
    if not os.path.exists(addons_path): os.mkdir(addons_path)
    for chat in plugin_channels:
        async for x in ultroid_bot.iter_messages(chat, search=".py", filter=InputMessagesFilterDocument):
            plugin = os.path.join(addons_path, x.file.name)
            await x.download_media(plugin)
            load_addons(plugin)

async def ready():
    from .. import asst, udB, ultroid_bot
    chat_id = udB.get_key("LOG_CHANNEL")
    MSG = f"<blockquote>🔥 xᴛᴇᴀᴍ-ᴜʀʙᴏᴛ ᴀᴄᴛɪᴠᴀᴛᴇᴅ 🔥\n Owner : {ultroid_bot.full_name}\n xteam-urbot : {UltVer}\n Python : {python_version()}</blockquote>"
    PHOTO = "https://files.catbox.moe/k9ljse.jpg"
    BTTS = [[Button.url("Support", "https://t.me/xteam_cloner"), Button.inline("Close", "closeit")]]
    await asst.send_message(chat_id, MSG, file=PHOTO, buttons=BTTS, parse_mode="html")

async def WasItRestart(udb):
    key = udb.get_key("_RESTART")
    if not key: return
    from .. import asst, ultroid_bot
    try:
        data = key.split("_")
        who = asst if data[0] == "bot" else ultroid_bot
        await who.edit_message(int(data[1]), int(data[2]), "Restarted Successfully.")
    except Exception: pass
    udb.del_key("_RESTART")

async def enable_inline(ultroid_bot, username):
    bf = "BotFather"
    await ultroid_bot.send_message(bf, "/setinline")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, f"@{username}")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "Search")

def _version_changes(udb):
    for _ in ["BOT_USERS", "BOT_BLS", "VC_SUDOS", "SUDOS", "CLEANCHAT", "LOGUSERS", "PLUGIN_CHANNEL", "CH_SOURCE", "CH_DESTINATION", "BROADCAST"]:
        key = udb.get_key(_)
        if key and str(key)[0] != "[":
            key_val = udb.get(_)
            new_ = [int(z) if z.isdigit() or (z.startswith("-") and z[1:].isdigit()) else z for z in key_val.split()]
            udb.set_key(_, new_)

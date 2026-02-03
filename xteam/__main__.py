import os
import sys
import time
import asyncio 
import xteam
from . import *
from pytgcalls import PyTgCalls
from telethon import TelegramClient 
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from .startup.connections import validate_session
from strings import get_string
from .fns.helper import bash, time_formatter, updater
from .startup.funcs import (
    WasItRestart,
    autopilot,
    customize,
    plug,
    ready,
    startup_stuff,
)
from .startup.loader import load_other_plugins 

def register_vc_handlers():
    from xteam.handlers import unified_update_handler 
    from xteam import call_py
    if call_py:
        call_py.on_update()(unified_update_handler)
    else:
        LOGS.warning("call_py not available, handler registration skipped.")

async def main_async():
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    base_path = os.path.dirname(os.path.abspath(__file__))

    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(os.path.join(base_path, "..", ".git"))
        and await updater()
    ):
        await bash("bash installer.sh") 
        os.execl(sys.executable, sys.executable, "-m", "xteam")

    await startup_stuff()

    ultroid_bot.me.phone = None 
    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")
    await autopilot()

    pmbot = udB.get_key("PMBOT")
    manager = udB.get_key("MANAGER")
    addons = udB.get_key("ADDONS") or Var.ADDONS
    vcbot_enabled = udB.get_key("VCBOT") or Var.VCBOT
    
    if HOSTED_ON == "okteto":
        vcbot_enabled = False

    if (HOSTED_ON == "termux" or udB.get_key("LITE_DEPLOY")) and udB.get_key("EXCLUDE_OFFICIAL") is None:
        _plugins = "autocorrect autopic audiotools compressor forcesubscribe fedutils gdrive glitch instagram nsfwfilter nightmode pdftools profanityfilter writer youtube"
        udB.set_key("EXCLUDE_OFFICIAL", _plugins)

    call_py = None
    if vcbot_enabled:
        VC_SESSION = udB.get_key("VC_SESSION") or Var.VC_SESSION
        if VC_SESSION:
            session = validate_session(VC_SESSION)
        elif HOSTED_ON == "heroku":
            LOGS.warning("VCBOT enabled but VC_SESSION is missing. VC Bot disabled.")
            vcbot_enabled = False
            session = None
        else:
            session = "xteam-music"
            LOGS.info("VCBOT enabled but VC_SESSION missing. Trying local session.")

        if session:
            try:
                bot = TelegramClient(
                    session=session,
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    connection=ConnectionTcpAbridged,
                    auto_reconnect=True,
                    connection_retries=None,
                )
                await bot.start() 
                vc_me = await bot.get_me()
                LOGS.info(f"Assistant Started as {vc_me.first_name}") 
                
                call_py = PyTgCalls(bot)
                await call_py.start()
                LOGS.info("PyTgCalls Client started successfully.")
                
                xteam.bot = bot
                xteam.call_py = call_py
            except (AuthKeyDuplicatedError, EOFError):
                LOGS.info(get_string("py_c3"))
                udB.del_key("VC_SESSION")
                call_py = None
            except Exception as er:
                LOGS.info("PyTgCalls Error. VC Bot disabled.")
                LOGS.exception(er)
                call_py = None

    await load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=call_py)
    await customize()

    if udB.get_key("PLUGIN_CHANNEL"):
        await plug(udB.get_key("PLUGIN_CHANNEL"))

    if not udB.get_key("LOG_OFF"):
        await ready()

    await WasItRestart(udB)
    LOGS.info(f"Took {time_formatter((time.time() - start_time)*1000)} to start")
    LOGS.info("xteam-urbot has been deployed!")

if __name__ == "__main__":
    ultroid_bot.start() 
    ultroid_bot.loop.create_task(main_async()) 
    asst.run()
        

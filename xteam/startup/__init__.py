import os
import sys
import platform
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(os.path.join(BASE_DIR, "plugins")):
    print(f"ERROR: 'plugins' folder not found at {os.path.join(BASE_DIR, 'plugins')}")
    sys.exit(1)

LOGS = getLogger("Xteam")
TelethonLogger = getLogger("Telethon")

from ..version import __version__ as __xteam__
from ._extra import _ask_input

def where_hosted():
    if os.getenv("DYNO"): return "heroku"
    if os.getenv("ANDROID_ROOT"): return "termux"
    return "VPS"

HOSTED_ON = where_hosted()
TelethonLogger.setLevel(WARNING)

_LOG_FORMAT = "%m/%d/%Y, %H:%M:%S | %(name)s [%(levelname)s] : %(message)s"
basicConfig(format=_LOG_FORMAT, level=INFO, handlers=[StreamHandler()])

_ask_input()

LOGS.info(f"Python: {platform.python_version()} | Xteam: {__xteam__} | Host: {HOSTED_ON}")

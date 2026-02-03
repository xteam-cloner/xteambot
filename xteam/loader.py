import contextlib
import glob
import os
from importlib import import_module
from logging import Logger
from . import LOGS
from .fns.tools import get_all_files

class Loader:
    def __init__(self, path="plugins", key="Official", logger: Logger = LOGS):
        if not os.path.isabs(path):
            self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        else:
            self.path = path
        self.key = key
        self._logger = logger

    def load(self, log=True, func=import_module, include=None, exclude=None, after_load=None, load_all=False):
        if not os.path.exists(self.path):
            self._logger.error(f"'{os.path.basename(self.path)}' folder not found!")
            return

        _single = os.path.isfile(self.path)
        if include:
            if log: self._logger.info("Including: {}".format("• ".join(include)))
            files = glob.glob(f"{self.path}/_*.py")
            for file in include:
                p = f"{self.path}/{file}.py"
                if os.path.exists(p): files.append(p)
        elif _single:
            files = [self.path]
        else:
            files = get_all_files(self.path, ".py") if load_all else glob.glob(f"{self.path}/*.py")
            if exclude:
                for p in exclude:
                    if not p.startswith("_"):
                        with contextlib.suppress(ValueError):
                            files.remove(f"{self.path}/{p}.py")

        if log and not _single:
            self._logger.info(f"⚙️ Load {self.key} Plugins || Count : {len(files)} •")

        for plugin in sorted(files):
            if func == import_module:
                path_split = plugin.replace(".py", "").split(os.sep)
                if "xteam" in path_split:
                    idx = path_split.index("xteam")
                    plugin = ".".join(path_split[idx:])
                else:
                    plugin = plugin.replace("/", ".").replace("\\", ".")
            
            try:
                modl = func(plugin)
            except ModuleNotFoundError as er:
                self._logger.error(f"{plugin}: '{er.name}' not installed!")
                continue
            except Exception as exc:
                self._logger.error(f"xteam - {self.key} - ERROR - {plugin}")
                self._logger.exception(exc)
                continue
            
            if _single and log:
                self._logger.info(f"Successfully Loaded {plugin}!")
            if callable(after_load):
                p_name = plugin.split(".")[-1] if func == import_module else plugin
                after_load(self, modl, plugin_name=p_name)
            

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
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.path = os.path.join(base_dir, path)
        else:
            self.path = path
        self.key = key
        self._logger = logger

    def load(
        self,
        log=True,
        func=import_module,
        include=None,
        exclude=None,
        after_load=None,
        load_all=False,
    ):
        if not os.path.exists(self.path):
            self._logger.error(f"'{self.path}' folder not found!")
            return

        _single = os.path.isfile(self.path)
        if include:
            if log:
                self._logger.info("Including: {}".format("• ".join(include)))
            files = glob.glob(f"{self.path}/_*.py")
            for file in include:
                p = f"{self.path}/{file}.py"
                if os.path.exists(p):
                    files.append(p)
        elif _single:
            files = [self.path]
        else:
            if load_all:
                files = get_all_files(self.path, ".py")
            else:
                files = glob.glob(f"{self.path}/*.py")
            if exclude:
                for p in exclude:
                    if not p.startswith("_"):
                        with contextlib.suppress(ValueError):
                            files.remove(f"{self.path}/{p}.py")

        if log and not _single:
            self._logger.info(f"⚙️ Load {self.key} Plugins || Count : {len(files)} •")

        for plugin in sorted(files):
            if func == import_module:
                base_pkg = "xteam." if "xteam" in self.path else ""
                rel_path = os.path.relpath(plugin, os.path.dirname(os.path.dirname(__file__)))
                plugin = rel_path.replace(".py", "").replace("/", ".").replace("\\", ".")
            
            try:
                modl = func(plugin)
            except ModuleNotFoundError as er:
                modl = None
                self._logger.error(f"{plugin}: '{er.name}' not installed!")
                continue
            except Exception as exc:
                modl = None
                self._logger.error(f"xteam - {self.key} - ERROR - {plugin}")
                self._logger.exception(exc)
                continue
            if _single and log:
                self._logger.info(f"Successfully Loaded {plugin}!")
            if callable(after_load):
                if func == import_module:
                    plugin = plugin.split(".")[-1]
                after_load(self, modl, plugin_name=plugin)
                

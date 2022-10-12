from importlib import import_module
import os
from typing import Union

from .base import BaseFormatter

def get_formatter(name: str) -> Union[BaseFormatter, None]:
    if not os.path.exists("formatters/" + name + ".py"):
        return None
    return import_module("formatters."+name).Formatter
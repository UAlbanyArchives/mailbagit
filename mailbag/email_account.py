from os import listdir
from os.path import dirname, basename, isfile, join
import sys

from abc import ABC, abstractmethod
class EmailAccount(ABC):
    """EmailAccount - abstract base class and registry for concrete email format parsers

    This class serves two purposes.  Firstly, it serves as an abstract base class, defining
    the methods and properties required by a parser that can parse data out of a particular
    on-disk email storage format for use by Mailbag.

    Secondly, it serves as a registry of such formats, with the goal of allowing new formats to
    be implemented in a "plug-in" fashion.  Any class subclassing this one, with the expected
    properties and a class variable "format_name" will be registered on this class and thus usable
    by the software."""

    # Registry of formats, key = cls.format_name, value = cls
    registry = {}

    def __init_subclass__(cls, **kwargs):
        """Enforce format_name attribute on subclasses, register them"""
        if not hasattr(cls, 'format_name'):
            raise RuntimeError("EmailAccount subclass must have `format_name` attribute")

        super().__init_subclass__(**kwargs)
        __class__.registry[cls.format_name] = cls

    @abstractmethod
    def __init__(self, target_account, **kwargs):
        """Implement a method that finds and sets up an account so that `account_data` and `messages` can
be called on it."""
        pass

    @abstractmethod
    def account_data(self):
        """Return a dict containing any data about the account as a whole that's relevant to mailbag processing."""
        pass

    @abstractmethod
    def messages(self):
        """Generator method that yields one message at a time from an email account as `Email`s."""
        pass

def import_formats(additional_dirs=None):
    if not additional_dirs:
        additional_dirs = []

    dirs = [join(dirname(__file__), 'formats'), *additional_dirs]

    for formats_dir in dirs:
        # put formats_dir at front of python load path for import
        sys.path.insert(0, formats_dir)

        try:
            for filename in listdir(formats_dir):
                module = basename(filename)[:-3]
                # skip if not a normal file ending in .py
                if module.startswith('_') or \
                   not isfile(join(formats_dir, filename)) or \
                   filename[-3:] != '.py':
                    continue
                __import__(module, globals(), locals())
        finally:
            sys.path = sys.path[1:]

import_formats()

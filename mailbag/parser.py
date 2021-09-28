from os import listdir
from os.path import dirname, basename, isfile, join

from abc import ABC, abstractmethod
class EmailFormatParser(ABC):
    """EmailFormatParser - abstract base class and registry for concrete format parsers

    This class serves two purposes.  Firstly, it serves as an abstract base class, defining
    the methods and properties required by a parser that can parse data out of a particular
    on-disk email storage format for use by Mailbag.

    Secondly, it serves as a registry of such formats, with the goal of allowing new formats to
    be implemented in a "plug-in" fashion.  Any class subclassing this one, with the expected
    properties and a class variable "parser_name" will be registered on this class and thus usable
    by the software."""

    # Registry of parsers, key = cls.parser_name, value = cls
    registry = {}

    def __init_subclass__(cls, **kwargs):
        """Enforce parser_name attribute on subclasses, register them"""
        if not hasattr(cls, 'parser_name'):
            raise RuntimeError("EmailFormatParser subclass must have `parser_name` attribute")

        super().__init_subclass__(**kwargs)
        __class__.registry[cls.parser_name] = cls

    @abstractmethod
    def parse(self, *args, **kwargs):
        """Implement a parse method that processes a concrete mail format (e.g. mbox, pst) and
        returns the information needed by mailbag to process that format"""
        pass

def import_parsers():
    parser_dir = join(dirname(__file__), 'parsers')

    for filename in listdir(parser_dir):
        module = basename(filename)

        if module.startswith('_') or not isfile(join(parser_dir, filename)):
            continue
        __import__('mailbag.parsers.' + module[:-3], globals(), locals())

import_parsers()
from os import listdir
from os.path import  basename, dirname, exists, isfile, join
from importlib.machinery import SourceFileLoader
import sys

from abc import ABC, abstractmethod
class Derivative(ABC):
    """Derivative - abstract base class and registry for concrete derivatives, which are processors that create new files or accomplish processing tasks based on the contents of a mailbox.

    This class serves two purposes.  Firstly, it serves as an abstract base class, defining
    the methods and properties required by a processor that produces derivatives for an EmailAccount.

    Secondly, it serves as a registry of such formats, with the goal of allowing new formats to
    be implemented in a "plug-in" fashion.  Any class subclassing this one, with the expected
    properties and a class variable "derivative_name" will be registered on this class and thus usable
    by the software."""

    # Registry of derivatives, key = cls.derivative_name, value = cls
    registry = {}

    def __init_subclass__(cls, **kwargs):
        """Enforce derivative descriptive attributes on subclasses, register them"""
        derivative_attrs = ["derivative_name", "derivative_format", "derivative_agent", "derivative_agent_version"]
        for attr in derivative_attrs:
            if not hasattr(cls, attr):
                raise RuntimeError("Derivative subclass must have `" + attr + "` attribute")

        super().__init_subclass__(**kwargs)
        __class__.registry[cls.derivative_name] = cls


    @abstractmethod
    def __init__(self, email_account, **kwargs):
        """Set up email account for use in processing methods.

        If not taking any other steps, the implementation of this can simple be `super()`
        """
        self.account = email_account


    @abstractmethod
    def do_task_per_account(self):
        """Perform any tasks that should happen once per whole account."""
        pass

    @abstractmethod
    def do_task_per_message(self, message):
        """Perform any tasks that should happen once per message"""
        pass

def import_derivatives(additional_dirs=None):
    if not additional_dirs:
        additional_dirs = []

    dirs = [join(dirname(__file__), 'derivatives'), *additional_dirs]

    for derivatives_dir in dirs:
        if not exists(derivatives_dir): continue

        for filename in listdir(derivatives_dir):
            module = basename(filename)[:-3]
            full_path = join(derivatives_dir, filename)
            # skip if not a normal, non underscored file ending in .py
            if module.startswith('_') or \
               not isfile(full_path) or \
               filename[-3:] != '.py':
                continue

            SourceFileLoader(module, full_path).load_module()

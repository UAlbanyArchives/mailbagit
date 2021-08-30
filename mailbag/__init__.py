# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"


from bagit import _make_parser
from gooey import Gooey

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbag ({bagit_parser.description})"

def cli():
    bagit_parser.parse_args()

@Gooey
def gui():
    bagit_parser.parse_args()

class Mailbag:
    def __init__(self):
        print("Hello world!")

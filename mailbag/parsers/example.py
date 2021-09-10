# This is an example parser, meant to show how
# to hook up a real parser

# Does nothing currently
from mailbag.parser import EmailFormatParser
class ExampleParser(EmailFormatParser):
    parser_name = 'example'

    def parse(self, *args, **kwargs):
        print("Parsity parse")

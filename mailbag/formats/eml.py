import datetime
import json
import eml_parser
from os.path import join
import mailbox
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email






log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""
    format_name = 'eml'

    def __init__(self, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        log.info("Reading : ", File=self.file)


    def account_data(self):
        return account_data

    def json_serial(obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()

            return serial

    def messages(self):

        with open(self.file, 'rb') as fhdl:
            raw_email = fhdl.read()

        ep = eml_parser.EmlParser()
        parsed_eml = ep.decode_email_bytes(raw_email)
        # print(dir(parsed_eml))
        c = json.dumps(parsed_eml, default=EML.json_serial)
        parsed_json = (json.loads(c))
        for i in parsed_json["header"]["header"]["message-id"]:
            Message = i
        for i in parsed_json["header"]["to"]:
            To = i
        for i in parsed_json["header"]["header"]["content-type"]:
            c=i



        message = Email(
                  Message_ID= Message,
                  # Email_Folder="",
                    Date=parsed_json["header"]["date"],
                    From=parsed_json["header"]["from"],
                    To=To,
                    #Cc=parsed_json["header"]["received_foremail"],
                    #Bcc=mail['Bcc'],
                    Subject=parsed_json["header"]["subject"],
                    Content_Type=c
                )

        yield message

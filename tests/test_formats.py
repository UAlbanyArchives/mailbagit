from mailbagit.controller import Controller
from mailbagit.models import Email
from argparse import Namespace
from mailbagit.email_account import EmailAccount
import mailbagit
import pytest
import email
import os

# This is a mock object representing the args returned from argparse/Gooey
@pytest.fixture
def cli_args():
    return Namespace(dry_run=True, mailbag_name="New_Mailbag", companion_files=False)


def test_Mbox(cli_args):
    testfile = "sample1.mbox"
    data = EmailAccount.registry["mbox"](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1][1:] + "-" + os.path.splitext(testfile)[0])

    for i, message in enumerate(data):
        message.Mailbag_Message_ID = i + 1
        expected = Email()
        expected.read(os.path.join(dump_dir, str(i + 1)))

        for field in message:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected, field[0])
                compare = getattr(message, field[0])
                if not dump is None and compare is None:
                    for key in compare:
                        assert compare[key] == dump[key]
            elif field[0] == "Attachments":
                for count, attachment in enumerate(message.Attachments):
                    match = False
                    for exp_attach in expected.Attachments:
                        if attachment.Name == exp_attach.Name:
                            match = True
                            for attachmentField in attachment:
                                dump = getattr(exp_attach, attachmentField[0])
                                compare = getattr(attachment, attachmentField[0])
                                if attachmentField[0] == "Content_ID":
                                    assert len(compare) > 0
                                else:
                                    assert dump == compare
                    assert match == True
            else:
                assert getattr(message, field[0]) == getattr(expected, field[0])


def test_MSG(cli_args):
    testfile = "Digitization Archiving Solutions.msg"
    data = EmailAccount.registry["msg"](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1][1:] + "-" + os.path.splitext(testfile)[0])

    for i, message in enumerate(data):
        message.Mailbag_Message_ID = i + 1
        expected = Email()
        expected.read(os.path.join(dump_dir, str(i + 1)))

        for field in message:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected, field[0])
                compare = getattr(message, field[0])
                if not dump is None and compare is None:
                    for key in compare:
                        assert compare[key] == dump[key]
            elif field[0] == "Attachments":
                for count, attachment in enumerate(message.Attachments):
                    match = False
                    for exp_attach in expected.Attachments:
                        if attachment.Name == exp_attach.Name:
                            match = True
                            for attachmentField in attachment:
                                dump = getattr(exp_attach, attachmentField[0])
                                compare = getattr(attachment, attachmentField[0])
                                if attachmentField[0] == "Content_ID":
                                    assert len(compare) > 0
                                else:
                                    assert dump == compare
                    assert match == True
            else:
                assert getattr(message, field[0]) == getattr(expected, field[0])


def test_EML(cli_args):

    testfile = "2016-06-23_144430_6e449c77fe.eml"
    data = EmailAccount.registry["eml"](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1][1:] + "-" + os.path.splitext(testfile)[0])

    for i, message in enumerate(data):
        message.Mailbag_Message_ID = i + 1
        expected = Email()
        expected.read(os.path.join(dump_dir, str(i + 1)))

        for field in message:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected, field[0])
                compare = getattr(message, field[0])
                if not dump is None and compare is None:
                    for key in compare:
                        assert compare[key] == dump[key]
            elif field[0] == "Attachments":
                for count, attachment in enumerate(message.Attachments):
                    match = False
                    for exp_attach in expected.Attachments:
                        if attachment.Name == exp_attach.Name:
                            match = True
                            for attachmentField in attachment:
                                dump = getattr(exp_attach, attachmentField[0])
                                compare = getattr(attachment, attachmentField[0])
                                if attachmentField[0] == "Content_ID":
                                    assert len(compare) > 0
                                else:
                                    assert dump == compare
                    assert match == True
            else:
                assert getattr(message, field[0]) == getattr(expected, field[0])


def test_PST(cli_args):
    if not "pst" in EmailAccount.registry:
        raise pytest.skip("PST not installed, cannot test")

    testfile = "outlook2019_MSO_16.0.10377.20023_64-bit.pst"
    data = EmailAccount.registry["pst"](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1][1:] + "-" + os.path.splitext(testfile)[0])

    for i, message in enumerate(data):
        message.Mailbag_Message_ID = i + 1
        expected = Email()
        expected.read(os.path.join(dump_dir, str(i + 1)))

        for field in message:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected, field[0])
                compare = getattr(message, field[0])
                if not dump is None and compare is None:
                    for key in compare:
                        assert compare[key] == dump[key]
            elif field[0] == "Attachments":
                for count, attachment in enumerate(message.Attachments):
                    match = False
                    for exp_attach in expected.Attachments:
                        if attachment.Name == exp_attach.Name:
                            match = True
                            for attachmentField in attachment:
                                dump = getattr(exp_attach, attachmentField[0])
                                compare = getattr(attachment, attachmentField[0])
                                if attachmentField[0] == "Content_ID":
                                    assert len(compare) > 0
                                else:
                                    assert dump == compare
                    assert match == True
            else:
                assert getattr(message, field[0]) == getattr(expected, field[0])

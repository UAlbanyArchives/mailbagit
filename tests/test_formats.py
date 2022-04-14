from mailbag.controller import Controller
from mailbag.models import Email
from argparse import Namespace
from mailbag.email_account import EmailAccount
import mailbag
import pytest
import email
import os

# This is a mock object representing the args returned from argparse/Gooey
@pytest.fixture
def cli_args():
    return Namespace(dry_run=True, mailbag_name="New_Mailbag")

def test_Mbox(cli_args):
    testfile = "sample1.mbox"
    data = EmailAccount.registry['mbox'](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1] + "-" + os.path.splitext(testfile)[0])

    expected = []
    for messageFile in os.listdir(dump_dir):
        message = Email()
        message.read(os.path.join(dump_dir, messageFile))
        expected.append(message)
    
    count = 0
    for id, m in enumerate(data):
        count += 1
        m.Mailbag_Message_ID = count

        for field in m:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected[id], field[0])
                compare = getattr(m, field[0])
                for key in compare:
                    assert compare[key] == dump[key]
            else:
                assert getattr(m, field[0]) == getattr(expected[id], field[0])
                


def test_MSG(cli_args):
    testfile = "sample1.msg"
    data = EmailAccount.registry['msg'](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1] + "-" + os.path.splitext(testfile)[0])

    expected = []
    for messageFile in os.listdir(dump_dir):
        message = Email()
        message.read(os.path.join(dump_dir, messageFile))

        expected.append(message)

    count = 0
    for id, m in enumerate(data):
        count += 1
        m.Mailbag_Message_ID = count

        for field in m:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected[id], field[0])
                compare = getattr(m, field[0])
                if compare:
                    for key in compare:
                        assert compare[key] == dump[key]
            else:
                assert getattr(m, field[0]) == getattr(expected[id], field[0])


def test_EML(cli_args):

    testfile = "2016-06-23_144430_6e449c77fe.eml"
    data = EmailAccount.registry['eml'](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1] + "-" + os.path.splitext(testfile)[0])

    expected = []
    for messageFile in os.listdir(dump_dir):
        message = Email()
        message.read(os.path.join(dump_dir, messageFile))

        expected.append(message)

    count = 0
    for id, m in enumerate(data):
        count += 1
        m.Mailbag_Message_ID = count

        for field in m:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected[id], field[0])
                compare = getattr(m, field[0])
                if compare:
                    for key in compare:
                        assert compare[key] == dump[key]
            else:
                assert getattr(m, field[0]) == getattr(expected[id], field[0])

def test_PST(cli_args):
    if not 'pst' in EmailAccount.registry:
        raise pytest.skip("PST not installed, cannot test")

    testfile = "outlook2019_MSO_16.0.10377.20023_64-bit.pst"
    data = EmailAccount.registry['pst'](os.path.join("data"), cli_args).messages()
    dump_dir = os.path.join("data", os.path.splitext(testfile)[1] + "-" + os.path.splitext(testfile)[0])

    expected = []
    for messageFile in os.listdir(dump_dir):
        message = Email()
        message.read(os.path.join(dump_dir, messageFile))

        expected.append(message)

    count = 0
    for id, m in enumerate(data):
        count += 1
        m.Mailbag_Message_ID = count

        for field in m:
            if field[0] == "Headers" or field[0] == "Message":
                dump = getattr(expected[id], field[0])
                compare = getattr(m, field[0])
                if compare:
                    for key in compare:
                        assert compare[key] == dump[key]
            else:
                assert getattr(m, field[0]) == getattr(expected[id], field[0])

from mailbag.controller import Controller
from mailbag.models import Email
import mailbag
import pytest
import os


def test_Mbox():
    data = mailbag.formats.mbox.Mbox(False, "New_Mailbag", os.path.join("data", "sample1.mbox")).messages()

    expected = []
    expected.append(Email(
        Content_Type='multipart/alternative; \n\tboundary="----=_Part_315462_994415758.1467289309709"',
        Date='Thu, 30 Jun 2016 12:22:39 +0000 (GMT)',
        From='Chuck Schumer <info@chuckschumer.com>',
        Message_ID='<1314145029.920292481467289359777.JavaMail.app@rbg21.atlis1>',
        Subject='=?utf-8?Q?The_GOP=E2=80=99s_horrendous_damage?=',
        To='ualbanymodernpoliticalarchives@gmail.com'
    ))
    expected.append(Email(
        Content_Type='multipart/alternative; boundary=94eb2c123e4c3234a50535f25ea8',
        Date='Thu, 23 Jun 2016 13:52:42 +0000',
        From='Andy from Google <andy-noreply@google.com>',
        Message_ID='<aad3793892b4891.1466689961655.100038985.377502.en.d9c49a37ba14f4e@google.com>',
        Subject='UAlbany, welcome to your new Google Account',
        To='ualbanymodernpoliticalarchives@gmail.com'
    ))

    for id, m in enumerate(data):
        assert m == expected[id]


def test_MSG():
    data = mailbag.formats.msg.MSG(False, "New_Mailbag", os.path.join("data", "sample1.msg")).messages()

    expected = []
    expected.append(Email(
        Date='Sat, 12 Aug 2006 14:25:25 -0400',
        From='John Doe <jdoes@someserver.com>',
        Subject='(outlookEMLandMSGconverter Trial Version Import) BitDaddys Software',
        To='sales@bitdaddys.com'
    ))

    for id, m in enumerate(data):
        assert m == expected[id]


def test_PST():
    data = mailbag.formats.pst.PST(False, "New_Mailbag", os.path.join("data", "outlook2019_MSO_16.0.10377.20023_64-bit.pst")).messages()

    expected = []
    expected.append(Email(
        Cc='gwiedeman@albany.edu',
        Content_Type='multipart/alternative; boundary=da8640888b204494a76c3a9e1f2a9112f911e113df090efab9b04e884486',
        Date='Thu, 30 Sep 2021 17:30:56 +0000 (UTC)',
        Email_Folder=os.path.join('Top of Outlook data file', 'Inbox', 'Today at UAlbany'),
        From='Today at UAlbany <tau@albany.edu>',
        Message_ID='<2Y2JQkdFSGmQAIdjAOswdQ@geopod-ismtpd-3-0>',
        Subject='Today at UAlbany - Focus on Research',
        To='gwiedeman@albany.edu'
    ))

    for id, m in enumerate(data):
        assert m == expected[id]
        break

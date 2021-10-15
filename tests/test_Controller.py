import pytest
from mailbag.controller import Controller
import mailbag
from mailbag.models import Email


def test_reader_Mbox():
    args = {}
    c = Controller(args)
    format, path = mailbag.formats.mbox.Mbox,"data/sample1.mbox"
    data = c.reader(format,path)
    
    expected = []
    expected.append(Email(
        Content_Type = 'multipart/alternative; \n\tboundary="----=_Part_315462_994415758.1467289309709"',
        Date = 'Thu, 30 Jun 2016 12:22:39 +0000 (GMT)',
        From = 'Chuck Schumer <info@chuckschumer.com>',
        Message_ID = '<1314145029.920292481467289359777.JavaMail.app@rbg21.atlis1>',
        Subject = '=?utf-8?Q?The_GOP=E2=80=99s_horrendous_damage?=', 
        To = 'ualbanymodernpoliticalarchives@gmail.com'
    )) 
    expected.append(Email(
        Content_Type = 'multipart/alternative; boundary=94eb2c123e4c3234a50535f25ea8',
        Date = 'Thu, 23 Jun 2016 13:52:42 +0000',
        From = 'Andy from Google <andy-noreply@google.com>',
        Message_ID = '<aad3793892b4891.1466689961655.100038985.377502.en.d9c49a37ba14f4e@google.com>', 
        Subject = 'UAlbany, welcome to your new Google Account',
        To = 'ualbanymodernpoliticalarchives@gmail.com'
    ))

    for id, m in enumerate(data):
        assert m == expected[id]

def test_reader_MSG():
    args = {}
    c = Controller(args)
    format, path = mailbag.formats.msg.MSG,"data/sample1.msg"
    data = c.reader(format,path)
    
    expected = []
    expected.append(Email(
        Date = 'Sat, 12 Aug 2006 14:25:25 -0400',
        From = 'John Doe <jdoes@someserver.com>',
        Subject = '(outlookEMLandMSGconverter Trial Version Import) BitDaddys Software',
        To = 'sales@bitdaddys.com'
    ))
    
    for id, m in enumerate(data):
        assert m == expected[id]

from jsonmodels import models, fields, errors, validators
from email.message import Message


class Attachment(models.Base):
    Name = fields.StringField()
    File = fields.EmbeddedField(bytes)
    MimeType = fields.StringField()

    
class Email(models.Base):
    """EmailModel - model class for email formats"""
    Error = fields.ListField(str)
    Mailbag_Message_ID = fields.IntField()
    Message_ID = fields.StringField()
    Original_File= fields.StringField()
    Message_Path = fields.StringField()
    Derivatives_Path = fields.StringField()
    Date = fields.StringField()
    From = fields.StringField()
    To = fields.StringField()
    Cc = fields.StringField()
    Bcc = fields.StringField()
    Subject = fields.StringField()
    Content_Type = fields.StringField()
    Headers = fields.EmbeddedField(Message)
    HTML_Body = fields.StringField()
    HTML_Encoding = fields.StringField()
    Text_Body = fields.StringField()
    Text_Encoding  = fields.StringField()
    Message = fields.EmbeddedField(Message)
    Attachments = fields.ListField(Attachment)
    StackTrace=fields.ListField(str)

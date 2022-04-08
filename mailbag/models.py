from jsonmodels import models, fields, errors, validators
from email.message import Message

class Email(models.Base):
    """EmailModel - model class for email formats"""
    Error = fields.ListField(str)
    Mailbag_Message_ID=fields.IntField()
    Message_ID = fields.StringField()
    Message_Path = fields.StringField()
    Original_Filename = fields.StringField()
    Date = fields.StringField()
    From = fields.StringField()
    To = fields.StringField()
    Cc = fields.StringField()
    Bcc = fields.StringField()
    Subject = fields.StringField()
    Content_Type = fields.StringField()
    Headers = fields.EmbeddedField(Message)
    HTML_Body = fields.StringField()
    HTML_Bytes = fields.EmbeddedField(bytes)
    Text_Body = fields.StringField()
    Text_Bytes = fields.EmbeddedField(bytes)
    Message = fields.EmbeddedField(Message)
    AttachmentNum = fields.IntField()
    AttachmentNames = fields.ListField(str)
    AttachmentFiles = fields.ListField(bytes)
    StackTrace=fields.ListField(str)

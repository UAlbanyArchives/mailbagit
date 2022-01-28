from jsonmodels import models, fields, errors, validators
from email.message import Message

class Email(models.Base):
    """EmailModel - model class for email formats"""
    Message_ID = fields.StringField()
    Email_Folder = fields.StringField()
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
    Text_Body = fields.StringField()
    Message = fields.EmbeddedField(Message)
    Error = fields.StringField()
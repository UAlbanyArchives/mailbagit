from jsonmodels import models, fields, errors, validators

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
    
    def __str__(self):
        email = {}
        try:
            
            '''TODO:  Improve efficiency'''
            email.update({"Message_ID":self.Message_ID,
                    "Email_Folder":self.Email_Folder,
                    "Original_Filename":self.Original_Filename,
                    "Date":self.Date,
                    "From":self.From,
                    "To":self.To,
                    "Cc":self.Cc,
                    "Bcc":self.Bcc,
                    "Subject":self.Subject,
                    "Content_Type":self.Content_Type
                    })
        except NameError: 
            print("Name error")
            
        return str(email)

from abc import ABC, abstractmethod
from jsonmodels import models, fields, errors, validators

class EmailModel(ABC):
    """EmailModel - abstract base model class for input data 
    """
    def __init__(self, *args,**kwargs):
        self.email = self.Email()
        pass
    
    class Email(models.Base):
        Message_ID = fields.StringField(required=True)
        Email_Folder = fields.StringField()
        Original_Filename = fields.StringField()
        Date = fields.StringField()
        From = fields.StringField()
        To = fields.StringField()
        Cc = fields.StringField()
        Bcc = fields.StringField()
        Subject = fields.StringField()
        Content_Type = fields.StringField()
    
    @abstractmethod
    def export(self, *args, **kwargs):
        """ 
        
        Args:
            'file' (key) : The file path to save JSON output
            
        Return:
            JSON data
        """
        
        pass
    
    
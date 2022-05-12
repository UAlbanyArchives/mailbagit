from jsonmodels import models, fields, errors, validators
from email.message import Message
import os, pickle


class Attachment(models.Base):
    Name = fields.StringField()
    File = fields.EmbeddedField(bytes)
    MimeType = fields.StringField()


class Email(models.Base):
    """EmailModel - model class for email formats"""

    Error = fields.ListField(str)
    Mailbag_Message_ID = fields.IntField()
    Message_ID = fields.StringField()
    Original_File = fields.StringField()
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
    Text_Encoding = fields.StringField()
    Message = fields.EmbeddedField(Message)
    Attachments = fields.ListField(Attachment)
    StackTrace = fields.ListField(str)

    def dump_string(self, value, outpath, encoding=None):
        with open(outpath + ".txt", "w", encoding="utf-8", newline="\n") as f:
            f.write(value)
            f.close()

    def dump(self):
        filename = os.path.basename(self.Original_File)
        dump_file = os.path.splitext(filename)[1][1:] + "-" + os.path.splitext(filename)[0]
        rootpath = os.path.join("data", dump_file, str(self.Mailbag_Message_ID))
        if not os.path.isdir(rootpath):
            os.makedirs(rootpath)

        for field in self:
            name = field[0]
            value = getattr(self, name)

            if value is None:
                pass
            elif isinstance(value, str) or isinstance(value, int):
                if name.endswith("_Body"):
                    encoding = getattr(self, name.split("_")[0] + "_Encoding")
                else:
                    encoding = None
                self.dump_string(str(value), os.path.join(rootpath, name), encoding)
            elif isinstance(value, list):
                count = 0
                for item in value:
                    count += 1
                    outdir = os.path.join(rootpath, name)
                    if not os.path.isdir(outdir):
                        os.mkdir(outdir)
                    outpath = os.path.join(outdir, str(count))
                    if isinstance(item, str):
                        self.dump_string(item, outpath)
                    else:
                        # attachment objects
                        if not os.path.isdir(outpath):
                            os.mkdir(outpath)
                        for subfield in item:
                            subname = subfield[0]
                            subvalue = getattr(item, subname)
                            if isinstance(subvalue, str):
                                self.dump_string(subvalue, os.path.join(outpath, subname))
                            elif isinstance(subvalue, bytes):
                                with open(os.path.join(outpath, subname + ".bin"), "wb") as f:
                                    f.write(subvalue)
                                    f.close()
            else:
                # Message and header objects
                outdir = os.path.join(rootpath, name)
                with open(outdir + ".pickle", "wb") as f:
                    pickle.dump(value, f)
                    f.close()

    def read_file(self, path, encoding, filetype="r"):
        if filetype == "r":
            with open(path, filetype, encoding="utf-8", newline="\n") as f:
                data = f.read()
                f.close()
        else:
            with open(path, filetype, encoding="utf-8") as f:
                data = f.read()
                f.close()
        return data

    def read(self, messagedir):
        for field in os.listdir(messagedir):
            fieldpath = os.path.join(messagedir, field)
            if os.path.isfile(fieldpath):
                # print (field)
                if field == "Headers.pickle" or field == "Message.pickle":
                    with open(fieldpath, "rb") as f:
                        value = pickle.load(f)
                        setattr(self, os.path.splitext(field)[0], value)
                        f.close()
                else:
                    if field.endswith("_Body.txt"):
                        encodingFile = os.path.join(messagedir, field.split("_")[0] + "_Encoding.txt")
                        encoding = self.read_file(encodingFile, None)
                    else:
                        encoding = None
                    value = self.read_file(fieldpath, encoding)
                    if field == "Mailbag_Message_ID":
                        setattr(self, os.path.splitext(field)[0], int(value))
                    else:
                        setattr(self, os.path.splitext(field)[0], value)
            else:
                subvalue = []
                for subfield in os.listdir(fieldpath):
                    subfieldpath = os.path.join(fieldpath, subfield)
                    if os.path.isfile(subfieldpath):
                        subvalue.append(self.read_file(subfieldpath, None))
                    else:
                        # attachments
                        attachment = Attachment()
                        for subsubfield in os.listdir(subfieldpath):
                            subsubfieldpath = os.path.join(subfieldpath, subsubfield)
                            if subsubfield == "File.bin":
                                filetype = "rb"
                            else:
                                filetype = "r"
                            setattr(
                                attachment,
                                os.path.splitext(subsubfield)[0],
                                self.read_file(subsubfieldpath, None, filetype),
                            )
                        subvalue.append(attachment)
                setattr(self, os.path.splitext(field)[0], subvalue)

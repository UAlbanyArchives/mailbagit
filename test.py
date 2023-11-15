import extract_msg
import chardet
import os
import bs4
import RTFDE
from striprtf.striprtf import rtf_to_text
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.de_encapsulate_html import De_encapsulate_HTML

# filePath = "/data/msg_bugs/issues/Creation of a Committee to Create Additional Funding Opportunities for UAlbany.msg"
filePath = "/data/msg_bugs/issues/FW SUNY-wide transfer in the major (1).msg"

# filePath = "/data/msg_bugs/new"
"""
for msg in os.listdir(filePath):
	if msg.endswith("msg"):
		print (msg)
		mail = extract_msg.openMsg(os.path.join(filePath, msg))
		body = mail.rtfBody
		print (chardet.detect(body))
		deencapsultor = RTFDE.DeEncapsulator(body)
		deencapsultor.deencapsulate()
"""
mail = extract_msg.openMsg(os.path.join(filePath))
# print (mail.sender)
# print (mail.to)

# print (mail.areStringsUnicode)

# print (mail.rtfBody)
# body = mail.rtfBody

"""
with open("/data/msg_bugs/issues/test-default.rtf", "wb") as f:
	f.write(body)
with open("/data/msg_bugs/issues/test-1252.rtf", "w") as f:
	f.write(body.decode("cp1252"))
with open("/data/msg_bugs/issues/test-950.rtf", "w") as f:
	f.write(body.decode("cp950"))
"""


# enc = chardet.detect(body)
# print (chardet.detect(body))

parser = Rtf_Parser(rtf_path="/data/msg_bugs/issues/rtf/test-default.rtf")
parsed = parser.parse_file()

renderer = De_encapsulate_HTML()
with open("/data/msg_bugs/issues/rtf/out.html", mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)

# deencapsultor = RTFDE.DeEncapsulator(body)
# deencapsultor.deencapsulate()


"""
if (mail.htmlBody):
	enc = chardet.detect(mail.htmlBody)
	print ("\t--> " + enc["encoding"])
	print (mail.htmlBody)
	#body = mail.htmlBody.decode('utf-8')
	#soup = bs4.BeautifulSoup(mail.htmlBody, 'html.parser')
	#meta = soup.find("meta")
	#print (meta)
	#try:
	#	body = mail.htmlBody.decode('cp1252')
	#except:
	#	body = mail.htmlBody.decode('utf-8')
	#print (body)
	#print (mail.stringEncoding)
	#print (mail.overrideEncoding)
	#print (dir(mail))
"""

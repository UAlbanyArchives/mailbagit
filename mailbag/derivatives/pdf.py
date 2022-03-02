import os
from subprocess import Popen, PIPE
from mailbag.derivative import Derivative


class ExampleDerivative(Derivative):
    derivative_name = 'pdf'

    def __init__(self, email_account, **kwargs):
        print("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message, args):
        wkhtmltopdf = 'wkhtmltopdf.exe'
        html = message.HTML_Body
        From_name=message.From.split("<")
        To_name=message.To.split("<")
        #htmlnew="<table>  <tr>    <th>From</th>    <th>To</th> </tr>"  + "<tr> <td>"+a+d[1][:-1]+"</td>"+"<td>"+b+c[1][:-1]+"</td>  </tr>"+"</table>"
        #Adding From and To fields in pdf
        html_from_to="From :"+"&nbsp"+ From_name[0]+ From_name[1][:-1]+"<br>"+"To:"+"&nbsp"+To_name[0]+To_name[1][:-1]
        html_name = os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".html")
        pdf_name =os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".pdf")
        write_html = open(html_name, 'w')
        write_html.write(html_from_to)
        write_html.write(html)
        write_html.close()
        #s = subprocess.run([wkhtmltopdf,html_name,pdf_name])
        p = Popen([wkhtmltopdf, html_name, pdf_name], stdout=PIPE, stderr=PIPE,universal_newlines=True)
        stdout, stderr = p.communicate()
        if len(stdout) > 0:
            print(stdout)
        if len(stderr) > 0:
            print(stderr)








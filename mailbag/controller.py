import mailbag
from parsers.mbox import Mbox


class Controller:
    """Controller - Main controller to start the program
    
    command line input sample:
    --input_type mbox --sha1 ../data/sample.mbox --input ../data/sample.mbox
    """
    def start(self):
        args = mailbag.cli()
        print(args)
        if(args.input_type == "mbox"):
            mb = Mbox()
            emails = mb.parse(file=args.input)
            
            for email in emails:
                print(email)        


if __name__ == '__main__':
    c = Controller()
    c.start()
    



class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args, formats):
        self.args = args
        self.format_map = {
                'mbox': formats.mbox.Mbox,
                'msg': formats.msg.MSG
        }
        
    def read(self):

        format = self.format_map[self.args.input](self.args)            
        messages = format.messages()
        for m in messages:
            print(m)

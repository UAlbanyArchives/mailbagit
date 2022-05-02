def init():
    global loglevel, style
    loglevel = 'WARN'
    style = {
                'g' : ['\033[92m','\033[0m'],   #green start and end
                'y' : ['\033[93m','\033[0m'],
                'b' : ['\033[1m','\033[0m']     # bold start and end
            }
    
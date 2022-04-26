def init():
    global session, processedSize, loglevel, style
    totalSize = 0
    processedSize = 0
    loglevel = 'WARN'
    style = {
                'g' : ['\033[92m','\033[0m'],   #green start and end
                'b' : ['\033[1m','\033[0m']     # bold start and end
            }
    
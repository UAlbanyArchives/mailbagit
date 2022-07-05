def init():
    global log_level, style
    log_level = "WARNING"
    style = {
        "g": ["\033[92m", "\033[0m"],  # green start and end
        "cy": ["\033[96m", "\033[0m"],
        "b": ["\033[1m", "\033[0m"],  # bold start and end
    }

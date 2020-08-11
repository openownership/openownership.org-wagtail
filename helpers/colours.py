# Background colours
BG = {
    'BLACK': '\033[40m',
    'RED': '\033[41m',
    'GREEN': '\033[42m',
    'ORANGE': '\033[43m',
    'BLUE': '\033[44m',
    'MAGENTA': '\033[45m',
    'CYAN': '\033[46m',
    'WHITE': '\033[47m',
}

RESET = '\x1b[0m'
BOLD = '\033[1m'

# Foreground colours
FG = {
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'ORANGE': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'DARKGREY': '\033[90m',
    'LIGHTRED': '\033[91m',
    'LIGHTGREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'LIGHTBLUE': '\033[94m',
    'PINK': '\033[95m',
    'LIGHTCYAN': '\033[96m'
}


def bg_black(msg):
    return '{}{}{}'.format(BG['BLACK'], msg, RESET)


def bg_red(msg):
    return '{}{}{}'.format(BG['RED'], msg, RESET)


def bg_green(msg):
    return '{}{}{}'.format(BG['GREEN'], msg, RESET)


def bg_orange(msg):
    return '{}{}{}'.format(BG['ORANGE'], msg, RESET)


def bg_blue(msg):
    return '{}{}{}'.format(BG['BLUE'], msg, RESET)


def bg_magenta(msg):
    return '{}{}{}'.format(BG['MAGENTA'], msg, RESET)


def bg_cyan(msg):
    return '{}{}{}'.format(BG['CYAN'], msg, RESET)


def bg_white(msg):
    return '{}{}{}'.format(BG['WHITE'], msg, RESET)


def black(msg):
    return '{}{}{}'.format(FG['BLACK'], msg, RESET)


def red(msg):
    return '{}{}{}'.format(FG['RED'], msg, RESET)


def green(msg):
    return '{}{}{}'.format(FG['GREEN'], msg, RESET)


def orange(msg):
    return '{}{}{}'.format(FG['ORANGE'], msg, RESET)


def blue(msg):
    return '{}{}{}'.format(FG['BLUE'], msg, RESET)


def magenta(msg):
    return '{}{}{}'.format(FG['MAGENTA'], msg, RESET)


def cyan(msg):
    return '{}{}{}'.format(FG['CYAN'], msg, RESET)


def white(msg):
    return '{}{}{}'.format(FG['WHITE'], msg, RESET)


def darkgrey(msg):
    return '{}{}{}'.format(FG['DARKGREY'], msg, RESET)


def lightred(msg):
    return '{}{}{}'.format(FG['LIGHTRED'], msg, RESET)


def lightgreen(msg):
    return '{}{}{}'.format(FG['LIGHTGREEN'], msg, RESET)


def yellow(msg):
    return '{}{}{}'.format(FG['YELLOW'], msg, RESET)


def lightblue(msg):
    return '{}{}{}'.format(FG['LIGHTBLUE'], msg, RESET)


def pink(msg):
    return '{}{}{}'.format(FG['PINK'], msg, RESET)


def lightcyan(msg):
    return '{}{}{}'.format(FG['LIGHTCYAN'], msg, RESET)


def bold(msg):
    return '{}{}{}'.format(BOLD, msg, RESET)


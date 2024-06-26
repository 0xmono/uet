import os
import sys
import subprocess as sp
import logging

ConfigExtension = ".cfg"
LogExtension = ".log"

class ColorEscapeStrings:
    RESET='\033[0m'
    BOLD='\033[01m'
    DISABLE='\033[02m'
    UNDERLINE='\033[04m'
    REVERSE='\033[07m'
    STRIKE_THROUGH='\033[09m'
    INVISIBLE='\033[08m'
    class ForeGround:
        BLACK='\033[30m'
        RED='\033[31m'
        GREEN='\033[32m'
        ORANGE='\033[33m'
        BLUE='\033[34m'
        PURPLE='\033[35m'
        CYAN='\033[36m'
        LIGHT_GREY='\033[37m'
        DARK_GREY='\033[90m'
        LIGHT_RED='\033[91m'
        LIGHT_GREEN='\033[92m'
        YELLOW='\033[93m'
        LIGHT_BLUE='\033[94m'
        PINK='\033[95m'
        LIGHT_CYAN='\033[96m'
    class BackGround:
        BLACK='\033[40m'
        RED='\033[41m'
        GREEN='\033[42m'
        ORANGE='\033[43m'
        BLUE='\033[44m'
        PURPLE='\033[45m'
        CYAN='\033[46m'
        LIGHT_GREY='\033[47m'

def init_arg_parser(parser):
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="debug or not debug")
    parser.add_argument("-D", "--onlydebug",
                        action="store_true", dest="onlyDebug", default=False,
                        help="is this only debug run with applying any changes")
    parser.add_argument("-g", "--nocolor",
                        action="store_true", dest="noColor", default=False,
                        help="disable color output")

# Custom logs formatter
class LogFormatter(logging.Formatter):
    FORMATTERS = {
        logging.CRITICAL: "!!!CRITICAL!!!: %(module)s.py_%(lineno)d: %(msg)s",
        logging.ERROR   : "ERROR: %(module)s.py_%(lineno)d: %(msg)s",
        logging.WARNING : "WARNING: %(module)s.py_%(lineno)d: %(msg)s",
        logging.DEBUG    : "DBG: %(module)s.py_%(lineno)d: %(msg)s",
        "DEFAULT"       : "%(msg)s",
        "DEFAULT_DEBUG" : "%(module)s.py_%(lineno)d: %(msg)s",
    }

    COLORS = {
        logging.CRITICAL: ColorEscapeStrings.ForeGround.PURPLE,
        logging.ERROR   : ColorEscapeStrings.ForeGround.RED,
        logging.WARNING : ColorEscapeStrings.ForeGround.YELLOW,
        logging.DEBUG   : ColorEscapeStrings.ForeGround.DARK_GREY,
    }

    def __init__(self, fmt="%(levelno)s: %(msg)s", use_color = True):
        logging.Formatter.__init__(self, fmt)
        self.use_color = use_color

    def format(self, record):
        defaultFormat = self.FORMATTERS['DEFAULT']
        if logging.root.level == logging.DEBUG:
            defaultFormat = self.FORMATTERS['DEFAULT_DEBUG']
        formatterStr = self.FORMATTERS.get(record.levelno, self.FORMATTERS['DEFAULT'])

        if self.use_color and record.levelno in self.COLORS:
            colorFormat = self.COLORS[record.levelno] + '{}' + ColorEscapeStrings.RESET
            formatterStr = colorFormat.format(formatterStr)

        formatter = logging.Formatter(formatterStr)
        return formatter.format(record)

def process_parsed_args(ParsedArgs):
    fmt = LogFormatter(use_color = not ParsedArgs.noColor)
    hdlr = logging.StreamHandler(sys.stdout)

    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)

    if ParsedArgs.debug or ParsedArgs.onlyDebug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    return ParsedArgs.onlyDebug

def add_parent_dir_to_sys_path(filePath):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(filePath)), os.pardir)))

def get_func_name() -> str:
    return sys._getframe(1).f_code.co_name

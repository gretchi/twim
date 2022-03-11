
MES_LEVEL_INFO                          = 0
MES_LEVEL_WARN                          = 1
MES_LEVEL_ERROR                         = 2

_level = 0
_message = ""


def set_mes(level, message):
    global _level
    global _message

    if message != "":
        _level = level
        _message = message


def get_mes():
    return _level, _message

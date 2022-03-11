
import os
import datetime
import unicodedata
import platform
import logging
import subprocess

import emoji

STANDARD_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
NLD_TWITTER_DATETIME_FORMAT = "%m %d %H:%M:%S %z %Y"
EN_MONTHS = {
    "Jan": "01"
    , "Feb": "02"
    , "Mar": "03"
    , "Apr": "04"
    , "May": "05"
    , "Jun": "06"
    , "Jul": "07"
    , "Aug": "08"
    , "Sep": "09"
    , "Oct": "10"
    , "Nov": "11"
    , "Dec": "12"
}

PLATFORM_WINDOWS    = "Windows"
PLATFORM_DRAWIN     = "Darwin"
PLATFORM_LINUX      = "Linux"
PLATFORM_CYGWIN     = "CYGWIN_NT"

OS_NAME_NT          = "nt"
OS_NAME_POSIX       = "posix"


def non_locale_dependent_strptime(text):
    en_month = text[4:7]
    numeric_month = EN_MONTHS[en_month]
    remaining = text[7:]
    timeformat = f"{numeric_month}{remaining}"

    return datetime.datetime.strptime(timeformat, NLD_TWITTER_DATETIME_FORMAT)


def strftime(dt_object, fmt=STANDARD_DATETIME_FORMAT):
    return dt_object.strftime(STANDARD_DATETIME_FORMAT)


def tweet_normalize(text, replace_emoji=False):
    text = text.replace("\n", "")
    text = remove_emoji(text)
    return text

def convertion_unit(value):
    if value >= 1000000:
        value = value / 1000000
        if value < 10:
            return f"{value:.1f}M"
        else:
            return f"{value: 3.0f}M"
    elif value >= 1000:
        value = value / 1000
        if value < 10:
            return f"{value:.1f}K"
        else:
            return f"{value: 3.0f}K"

    return f"{value: 4d}"


def remove_emoji(text):
    return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)


def omiit_text(text, max_length, offset=0):
    scrape_text = ""
    current_length = 0

    for c in text:
        if unicodedata.east_asian_width(c) in "FWA":
            # マルチバイト文字
            current_length += 2
        else:
            # シングルバイト文字
            current_length += 1

        if current_length > max_length - offset - 2:
            scrape_text += ".."
            break

        scrape_text += c

    return scrape_text


def get_text_width(text):
    current_length = 0

    for c in text:
        if unicodedata.east_asian_width(c) in "FWA":
            # マルチバイト文字
            current_length += 2
        else:
            # シングルバイト文字
            current_length += 1

    return current_length


def text_to_turnback_list(text, width):
    current_length = 0
    line_buf = ""
    turnback_list = []

    for c in text:
        if unicodedata.east_asian_width(c) in "FWA":
            # マルチバイト文字
            current_length += 2
        else:
            # シングルバイト文字
            current_length += 1

        if c not in ("\n", "\r"):
            line_buf += c

        if current_length > width or c in ("\n", "\r"):
            turnback_list.append(line_buf)
            line_buf = ""
            current_length = 0
    else:
        turnback_list.append(line_buf)

    return turnback_list



def get_char_size(char):
    return len(char.encode())


def get_platform():
    return platform.system().split("-")[0]

def get_os_name():
    return os.name


def open_url(url):
    cmd = None
    pf = get_platform()

    if pf == PLATFORM_WINDOWS:
        cmd = ["start", url]
    elif pf == PLATFORM_DRAWIN:
        cmd = ["open", url]
    elif pf == PLATFORM_LINUX:
        cmd = ["xdg-open", url]
    elif pf == PLATFORM_CYGWIN:
        cmd = ["cygstart", url]

    exec_cmd(cmd)


def exec_cmd(cmd):
    logging.info(f"Execute command: {cmd}")

    try:
        subprocess.run(cmd)
    except Exception as e:
        logging.error(e)

        return False, str(e)

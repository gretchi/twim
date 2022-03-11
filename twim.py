#!/usr/bin/env python3

import os
import sys
import curses
import curses.ascii
import logging
import pprint
import locale
import time

from screen import Screen
from components import TimelineWindow, TimelineHeaderWindow, StatusBarWindow, DetailWindow, TweetInputWindow, TwimHelpWindow
from twitter import Twitter
from operation import Operation
from const import const
from util import system_message

__copyright__    = 'Copyright (C) 2019 syamamura'
__version__      = '1.0.0'
__license__      = 'MIT License'
__author__       = 'gretchi'
__author_email__ = 'randozou@gmail.com'
__url__          = 'https://github.com/gretchi/twim'

os.makedirs("./log/", exist_ok=True)
logging.basicConfig(filename="./log/twim.log", level=logging.INFO, format='%(levelname)s: %(asctime)s: %(message)s')
locale.setlocale(locale.LC_ALL, '')


# Twim-Client
CONSUMER_API_KEY = "q04UcTYpljTrzizsGYi4v0Prq"
CONSUMER_API_SECRET = "RnwgewYPjcIYvYXpsTzxHYgbBwMucZ8BkkKGHoU4uFBjtJXD8A"

TIMEZONE = "Asia/Tokyo"

class Twim(object):
    def __init__(self, stdscr):
        self.screen = Screen(stdscr)
        self.timezone = TIMEZONE
        self.twitter  = Twitter(CONSUMER_API_KEY, CONSUMER_API_SECRET, self.timezone)
        self.operation = Operation(self.screen, stdscr, self.twitter)



    def run(self):
        is_screen_size_changed = False

        header_window = TimelineHeaderWindow(self, self.screen, 1, 0, 0, 0)
        status_window = StatusBarWindow(self, self.screen, 0, 0, -2, 0)
        timeline_window = TimelineWindow(self, self.screen, -10, 0, 1, 0)
        detail_window = DetailWindow(self, self.screen, 8, 0, -10, 0)
        # help_window = TwimHelpWindow(self, self.screen, 30, 100, int(self.screen.max_rows / 2 - 15), int(self.screen.max_cols / 2 - 50))
        # tweet_window = TweetInputWindow(self, self.screen, 10, 0, 0, 0)


        while True:
            # ================================================================
            # 初期化
            # ================================================================
            # ウィンドウサイズ取得
            is_screen_size_changed = self.screen.update_max_screen_change()

            if is_screen_size_changed:
                time.sleep(0.2)
                continue

            if is_screen_size_changed:
                self.screen.resize_all()
                is_screen_size_changed = False
                continue


            # ================================================================
            # TL取得
            # ================================================================
            # タイムライン取得
            self.twitter.update_timeline()


            # ================================================================
            # ユーザ操作
            # ================================================================
            self.operation.operation()



            # ================================================================
            # 描画
            # ================================================================

            self.screen.draw_all()
            self.screen.refresh_all()


            # ================================================================
            # クローズ処理
            # ================================================================
            # self.twitter.update_current_tweet_id()
            self.twitter.update_unread()


            curses.napms(32)




def main(stdscr):
    try:
        twim = Twim(stdscr)
        twim.run()

    except Exception as e:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

        import traceback
        sys.stderr.writelines(traceback.format_exc())
        sys.stderr.writelines(str(e))
        sys.stderr.writelines("\n")

    except KeyboardInterrupt:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()



if __name__ == "__main__":
    curses.wrapper(main)

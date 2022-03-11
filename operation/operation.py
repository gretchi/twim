
import os
import sys
import tty
import fcntl
import termios
import signal
import subprocess
import logging

from const import const
from components import TwimHelpWindow, TweetInputWindow, FindTweetWindow
from util import system_message, helper


PLATFORM_WINDOWS    = "Windows"
PLATFORM_DRAWIN     = "Darwin"
PLATFORM_LINUX      = "Linux"
PLATFORM_CYGWIN     = "CYGWIN_NT"

OS_NAME_NT          = "NT"
OS_NAME_POSIX       = "POSIX"

KEY_CTRL            = 0x1f


class Operation(object):
    def __init__(self, screen, stdscr, twitter):
        self.pf      = helper.get_platform
        self.pid     = os.getpid()
        self._screen = screen
        self._stdscr = stdscr
        self.twitter = twitter

        self._fd = None
        self._old_attr = None

        self._is_show_help = False
        self._is_show_tweet_window = False
        self.find_regex_object = None


    def tty_raw_open(self):
        self._fd = sys.stdin.fileno()
        self._old_attr = termios.tcgetattr(self._fd)
        tty.setraw(sys.stdin.fileno())
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)


    def tty_raw_close(self):
        termios.tcsetattr(self._fd, termios.TCSANOW, self._old_attr)


    def operation(self):
        key_cd = self._stdscr.getch()

        if key_cd != 0x0A:
            logging.debug(f"Key input 1: 0x{key_cd:02X}")


        if key_cd == ord('k'):
            # カーソルを上へ移動
            self.twitter.decrement_cursor()

        elif key_cd == ord('j'):
            # カーソルを下へ移動
            self.twitter.increment_cursor()

        elif key_cd == ord('h'):
            # 以降の同一ユーザの発言
            self.twitter.jump_to_next_same_user()

        elif key_cd == ord('l'):
            # 以前の同一ユーザの発言
            self.twitter.jump_to_prev_prev_user()

        elif key_cd == ord('o'):
            # ツイートのURLを開く
            helper.open_url(self.twitter.get_url_tweet_status_by_tweet_id(self.twitter.current_tweet_id))

        elif key_cd == ord('p'):
            # プロフィールのURLを開く
            helper.open_url(self.twitter.get_url_user_profile_by_tweet_id(self.twitter.current_tweet_id))

        elif key_cd == ord(' '):
            # 未読ツイートへジャンプ
            self.twitter.jump_to_unread_tweet()

        elif key_cd == 0x13 or key_cd == -0x61:
            # ファボ切り替え
            if os.name == OS_NAME_POSIX:
                # 再開シグナル送信
                os.killpg(self.pid, signal.SIGCONT)

            self.twitter.toggle_favorite()

        elif key_cd == -0x52:
            # リツイート
            self.twitter.retweet()


        elif key_cd == ord('s'):
            # ヘルプ表示
            self.toggle_help()

        elif key_cd == ord('t'):
            # ツイートする
            # self.toggle_tweet_window()
            self.tweet_window = TweetInputWindow(self, self._screen, 10, 80, int(self._screen.max_rows / 2 - 5), int(self._screen.max_cols / 2 - 40))
            self.tweet_window.draw()
            logging.debug(f"Tweet input window result: (is_do_tweet: {self.tweet_window.is_do_tweet}, in_reply_to_status_id: {self.tweet_window.in_reply_to_status_id}, text: {self.tweet_window.text})")

            logging.debug(f"self.tweet_window.is_do_tweet: {self.tweet_window.is_do_tweet}")

            if self.tweet_window.is_do_tweet:
                self.send_tweet(self.tweet_window.text)

        elif key_cd == ord('r'):
            # 返信
            if self.twitter.current_tweet_id:
                self.tweet_window = TweetInputWindow(self, self._screen, 10, 80, int(self._screen.max_rows / 2 - 5), int(self._screen.max_cols / 2 - 40))
                self.tweet_window.set_mention(self.twitter.current_tweet_id, self.twitter.current_user_screen_name)
                self.tweet_window.draw()

                logging.debug(f"Tweet input window result: (is_do_tweet: {self.tweet_window.is_do_tweet}, in_reply_to_status_id: {self.tweet_window.in_reply_to_status_id}, text: {self.tweet_window.text})")

                if self.tweet_window.is_do_tweet:
                    self.send_tweet(self.tweet_window.text, self.tweet_window.in_reply_to_status_id)

        elif key_cd == ord('/'):
            # 検索
            find_window = FindTweetWindow(self, self._screen, 6, 80, int(self._screen.max_rows / 2 - 3), int(self._screen.max_cols / 2 - 40))
            find_window.draw()
            self.find_regex_object = find_window.regex

            if self.find_regex_object is not None:
                # 次
                self.twitter.goto_find_next(self.find_regex_object)

        elif key_cd == ord('n'):
            # 順検索
            if self.find_regex_object is not None:
                self.twitter.goto_find_next(self.find_regex_object)

        elif key_cd == ord('N'):
            # 逆検索
            if self.find_regex_object is not None:
                self.twitter.goto_find_prev(self.find_regex_object)

        elif key_cd == ord('g'):
            # カーソルを先頭へ移動
            self.twitter.jump_to_first()

        elif key_cd == ord('G'):
            # カーソルを行末へ移動
            self.twitter.jump_to_last()

        elif key_cd == 0x1D:
            # 再描画
            self._stdscr.clear()



        elif key_cd == 0x03:
            # 終了
            exit(0)

        return

    def toggle_help(self):
        if not self._is_show_help:
            self.help_window = TwimHelpWindow(self, self._screen, 30, 50, int(self._screen.max_rows / 2 - 15), int(self._screen.max_cols / 2 - 25))
            self._is_show_help = True
        else:
            self._screen.destroy_window(self.help_window.window_id)
            self._is_show_help = False

    def toggle_tweet_window(self):
        if not self._is_show_tweet_window:
            self.tweet_window = TweetInputWindow(self, self._screen, 10, 80, int(self._screen.max_rows / 2 - 5), int(self._screen.max_cols / 2 - 40))
            self._is_show_tweet_window = True
        else:
            self._screen.destroy_window(self.tweet_window.window_id)
            self._is_show_tweet_window = False

    def send_tweet(self, status, in_reply_to_status_id=None):
        logging.debug("Call operation.send_tweet()")

        return self.twitter.send_tweet(status, in_reply_to_status_id)

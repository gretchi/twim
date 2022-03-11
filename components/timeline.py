
import curses

from .components_base import ComponentsBase
from const import const
from util import helper


class TimelineWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)
        self.window.scrollok(True)


    def draw(self):
        self.window.setscrreg(0, self.height - 1)
        self.window.scroll(self._parent.twitter.cursor)

        for row, tweet in enumerate(self._parent.twitter.timeline_itar_pageing(self.height)):
            text_style          = const.COLOR_SET_DEFAULT
            rt_style            = const.COLOR_SET_RT
            fav_style           = const.COLOR_SET_FAV
            screen_name_style   = const.COLOR_SET_SCREEN_NAME
            timestamp_style     = const.COLOR_SET_TIME

            screen_name = f"@{tweet.user_screen_name}"
            text_raw = tweet.text
            creates_at_str = tweet.creates_at_str


            if tweet.favorited:
                # Fav
                text_style = const.COLOR_SET_FAV

            elif tweet.is_retweet:
                # RT
                text_style = const.COLOR_SET_RT
                screen_name = f"@{tweet.origin_user_screen_name}(RT:@{tweet.user_screen_name})"
                text_raw = tweet.origin_text
                creates_at_str = tweet.origin_creates_at_str

            elif not tweet.following:
                # FF外
                text_style = const.COLOR_SET_OUT_OF_FF

            if self._parent.twitter.current_tweet_id == tweet.tweet_id:
                text_style          = const.COLOR_SET_CURRENT
                rt_style            = const.COLOR_SET_CURRENT
                fav_style           = const.COLOR_SET_CURRENT
                screen_name_style   = const.COLOR_SET_CURRENT
                timestamp_style     = const.COLOR_SET_CURRENT
                self.window.hline(row, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_CURRENT))

            elif self._parent.twitter.current_user_id == tweet.user_id:
                text_style          = const.COLOR_SET_SAME_USER
                rt_style            = const.COLOR_SET_SAME_USER
                fav_style           = const.COLOR_SET_SAME_USER
                screen_name_style   = const.COLOR_SET_SAME_USER
                timestamp_style     = const.COLOR_SET_SAME_USER
                self.window.hline(row, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_SAME_USER))

            else:
                self.window.hline(row, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_DEFAULT))

            if tweet.unread:
                unread_mark  = "*"
            else:
                unread_mark  = ""


            self.window.addstr(row, 53, helper.omiit_text(helper.tweet_normalize(text_raw), self.width, 53), curses.color_pair(text_style))
            self.window.addstr(row, 51, unread_mark, curses.color_pair(text_style))
            self.window.addstr(row, 46, helper.convertion_unit(tweet.retweet_count), curses.color_pair(rt_style))
            self.window.addstr(row, 41, helper.convertion_unit(tweet.favorite_count), curses.color_pair(fav_style))
            self.window.addnstr(row, 20, helper.omiit_text(screen_name, 40, 20), 40, curses.color_pair(screen_name_style))
            self.window.addstr(row, 0, creates_at_str, curses.color_pair(timestamp_style))

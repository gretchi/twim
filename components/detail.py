
import curses

from .components_base import ComponentsBase
from const import const
from util import helper


class DetailWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)


    def draw(self):
        tweet = self._parent.twitter.get_current_tweet()
        if tweet is None:
            return

        uname_style = const.COLOR_SET_DETAIL_TOP_DEFAULT

        if tweet.favorited:
            uname_style = const.COLOR_SET_DETAIL_TOP_DEFAULT_FAV
        elif tweet.is_retweet:
            uname_style = const.COLOR_SET_DETAIL_TOP_DEFAULT_RT
        elif not tweet.following:
            uname_style = const.COLOR_SET_DETAIL_TOP_DEFAULT_OUT_OF_FF


        if tweet.is_retweet:
            # RT
            uname = f"{tweet.origin_user_name}/@{tweet.origin_user_screen_name}  (RT: {tweet.user_name}/@{tweet.user_screen_name} )"
            creates_at_str = helper.strftime(tweet.origin_created_at_dt)
            text_raw = tweet.origin_text

        else:
            # 通常
            uname = f"{tweet.user_name}/@{tweet.user_screen_name}"
            creates_at_str = helper.strftime(tweet.created_at_dt)
            text_raw = tweet.text

        src_and_create = f"{creates_at_str}  {tweet.source_name}"

        for row in range(self.height - 1):
            self.window.hline(row + 1, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_DEFAULT))

        self.window.hline(0, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT))
        self.window.addnstr(0, 0, uname, self.width, curses.color_pair(uname_style))
        self.window.addstr(0, self.width - len(src_and_create) - 1, src_and_create, curses.color_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT))

        for row, line in enumerate(helper.text_to_turnback_list(text_raw, self.width - 2)):
            self.window.addnstr(row + 1, 0, line, self.width)

            if row >= self.height - 3:
                break

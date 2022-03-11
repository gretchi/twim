
import curses

from .components_base import ComponentsBase
from const import const
from util import helper

HELP_WORDS = [
    ("Key", "  Assign")
    , ("t", ": Tweet")
    , ("r", ": Reply")
    , ("s", ": Show help")
    , ("k", ": One new a tweet")
    , ("j", ": One old a tweet")
    , ("h", ": New Tweet of the same user")
    , ("l", ": Old Tweet of the same user")
    , ("o", ": Open the Tweet URL")
    , ("p", ": Open the profile URL")
    , ("/", ": Find a Tweet")
    , ("n", ": Find (Next)")
    , ("N", ": Find (Previous)")
    , ("SPC", ": Jump to unread tweet")
    , ("C-s", ": Favorite")
    , ("C-r", ": Retweet")
    , ("C-c", ": Quit")
    , ("C-5", ": Force redraw of the screen")
    , ("", "")
    , ("GitHub:", "")
    , ("  https://github.com/gretchi/twim", "")
    , ("", "")
    , ("License:", "")
    , ("  This software is licensed under MIT License.", "")
]

class TwimHelpWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)


    def draw(self):
        self.window.border()
        self.window.addstr(0, int(self.width / 2 - len(" H E L P ") / 2), " H E L P ")

        for i, v in enumerate(HELP_WORDS):
            key, helpstring = v
            self.window.addstr(3 + i, 5, key)
            self.window.addstr(3 + i, 15, helpstring)

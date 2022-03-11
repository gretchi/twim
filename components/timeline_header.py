
import curses

from .components_base import ComponentsBase
from const import const
from util import helper


class TimelineHeaderWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)


    def draw(self):
        self.window.hline(0, 0, " ", self.width, curses.color_pair(const.COLOR_SET_HEADER_STYLE))

        self.window.addstr(0, 53, "Body", curses.color_pair(const.COLOR_SET_HEADER_STYLE))
        self.window.addstr(0, 50, " ", curses.color_pair(const.COLOR_SET_HEADER_STYLE))
        self.window.addstr(0, 46, "  RT", curses.color_pair(const.COLOR_SET_HEADER_STYLE))
        self.window.addstr(0, 41, " Fav", curses.color_pair(const.COLOR_SET_HEADER_STYLE))
        self.window.addstr(0, 20, "Screen name", curses.color_pair(const.COLOR_SET_HEADER_STYLE))
        self.window.addstr(0, 0, "Timestamp", curses.color_pair(const.COLOR_SET_HEADER_STYLE))

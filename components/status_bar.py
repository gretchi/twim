
import curses

from .components_base import ComponentsBase
from const import const
from util import helper
from util import system_message


class StatusBarWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)


    def draw(self):
        api_status_style = const.COLOR_SET_API_NORMAL
        if self._parent.twitter.api_remaining <= 0:
            api_status_style = const.COLOR_SET_API_ALART
        elif self._parent.twitter.api_remaining <= 3:
            api_status_style = const.COLOR_SET_API_WARN

        sys_mes_level, sys_mes_message = system_message.get_mes()

        api_status_message      = f"  API {self._parent.twitter.api_remaining: 2d}/{self._parent.twitter.api_limit: 2d} "
        update_at_message       = f"  Update at {self._parent.twitter.update_at}, Next {self._parent.twitter.next_update - self._parent.twitter.now_epoch} sec "
        system_message_text     = helper.omiit_text(f"  {sys_mes_message}  ", int(self.width / 2))
        system_message_style    = const.COLOR_SET_STATUS_BAR_INFO
        if sys_mes_level == system_message.MES_LEVEL_WARN:
            system_message_style = const.COLOR_SET_STATUS_BAR_WARN
        elif sys_mes_level == system_message.MES_LEVEL_ERROR:
            system_message_style = const.COLOR_SET_STATUS_BAR_ERROR


        self.window.hline(0, 0, ' ', self.width, curses.color_pair(const.COLOR_SET_STATUS_BAR))
        self.window.hline(1, 0, ' ', self.width)

        self.window.addstr(0, 0, " TIMELINE ", curses.color_pair(const.COLOR_SET_MODE))
        self.window.addstr(0, 11, f"[r: {self._parent.twitter.cursor}]", curses.color_pair(const.COLOR_SET_STATUS_BAR))
        self.window.addstr(0, self.width - len(api_status_message), api_status_message, curses.color_pair(api_status_style))
        self.window.addstr(0, self.width - len(api_status_message) - len(update_at_message), update_at_message, curses.color_pair(const.COLOR_SET_STATUS_BAR_TIME))
        # self.window.addstr(0, self.width - len(api_status_message) - len(update_at_message) - len(system_message), system_message, curses.color_pair(const.COLOR_SET_STATUS_BAR_SYSTEM_MES))

        self.window.addnstr(1, 0, system_message_text, self.width - 1, curses.color_pair(system_message_style))

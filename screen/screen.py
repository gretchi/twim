
import os
import curses
import shutil
import logging

from const import const



class Screen(object):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.max_rows  = 0
        self.max_cols  = 0
        self.current_window_id = 0

        self._init_curses()
        self.update_max_screen_change()

        self.components = []
        self.window_ids = []


    def regist_window(self, component):
        self.components.append(component)
        component.window_id = self.current_window_id

        component_id = len(self.components) - 1
        self.window_ids.append(component_id)
        self.current_window_id += 1

        logging.info(f"Regist window: ({component.__class__.__name__}, window_id: {self.current_window_id}, component_id: {component_id})")


    def destroy_window(self, window_id):
        component_id = self.window_ids[window_id]
        if component_id is not None:
            self.components[component_id].window.clear()
            self.components[component_id].panel.bottom()

            if not self.components[component_id].panel.hidden():
                self.components[component_id].panel.hide()

            del(self.components[component_id])
            self.window_ids[window_id] = None

        self.force_refresh_all()

        logging.info(f"Destroy window: (window_id: {window_id}, component_id: {component_id})")

    def refresh_all(self):
        curses.panel.update_panels()
        for component in self.components:
            component.refresh()


    def force_refresh_all(self):
        curses.panel.update_panels()
        for component in self.components:
            component.force_refresh()


    def draw_all(self):
        for component in self.components:
            if component.set_show:
                component.draw()
            else:
                component.window.clear()


    def update_max_screen_change(self):
        term_size = shutil.get_terminal_size()
        y = term_size.lines
        x = term_size.columns

        is_changed = False
        if self.max_rows != y or self.max_cols != x:
            is_changed = True

        self.max_rows = y
        self.max_cols = x

        self.resize_stdscr(y, x)

        if is_changed:
            logging.info(f"Detect terminal size change: (rows: {y}, cols: {x})")

        return is_changed

    def resize_stdscr(self, row, col):
        self.stdscr.resize(row, col)


    def resize_all(self):
        for component in self.components:
            component.resize()


    def _init_curses(self):
        os.environ.setdefault("ESCDELAY", "25")

        if curses.has_colors():
            curses.start_color()

        curses.nocbreak()
        curses.curs_set(0)
        curses.nl()

        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        curses.init_color(const.COLOR_USER_LIGHT, 600, 600, 600)
        curses.init_color(const.COLOR_USER_WHITESMOKE, 400, 400, 400)
        curses.init_color(const.COLOR_USER_GAINSBORO, 200, 200, 200)

        curses.init_pair(const.COLOR_SET_TIME, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_SCREEN_NAME, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_FAV, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_RT, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_OUT_OF_FF, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_API_NORMAL, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(const.COLOR_SET_API_WARN, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(const.COLOR_SET_API_ALART, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(const.COLOR_SET_MODE, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(const.COLOR_SET_CURRENT, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(const.COLOR_SET_STATUS_BAR, curses.COLOR_WHITE, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_STATUS_BAR_TIME, curses.COLOR_WHITE, const.COLOR_USER_WHITESMOKE)
        curses.init_pair(const.COLOR_SET_STATUS_BAR_SYSTEM_MES, curses.COLOR_RED, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT, curses.COLOR_WHITE, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT_FAV, curses.COLOR_RED, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT_RT, curses.COLOR_GREEN, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_DETAIL_TOP_DEFAULT_OUT_OF_FF, curses.COLOR_BLUE, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_HEADER_STYLE, const.COLOR_USER_LIGHT, const.COLOR_USER_GAINSBORO)
        curses.init_pair(const.COLOR_SET_STATUS_BAR_INFO, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_STATUS_BAR_WARN, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_STATUS_BAR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(const.COLOR_SET_SAME_USER, curses.COLOR_BLACK, const.COLOR_USER_LIGHT)

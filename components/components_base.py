
import curses
import curses.panel

class ComponentsBase(object):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        self._nlines    = nlines
        self._ncols     = ncols
        self._begin_y   = begin_y
        self._begin_x   = begin_x
        self._parent    = parent
        self._screen    = screen
        self._stdscr    = screen.stdscr
        self.window_id  = -1
        self.height     = 0
        self.width      = 0
        self.window     = self.create_window()
        self.panel      = curses.panel.new_panel(self.window)

        self.update_window_size()
        self._screen.regist_window(self)
        self.set_show()


    def create_window(self):
        new_size = self.get_new_windows_size()
        window = curses.newwin(*new_size)

        return window

    def resize(self):
        new_size = self.get_new_windows_size()
        self.window.resize(*new_size)
        self.update_window_size()

    def toggle_show_hide(self):
        if self.panel.hidden():
            self.panel.show()
        else:
            self.panel.hide()

    def set_show(self):
        if self.panel.hidden():
            self.panel.show()
            self.panel.top()


    def set_hide(self):
        if not self.panel.hidden():
            self.panel.hide()
            self.panel.bottom()


    def refresh(self):
        if self.window.is_wintouched():
            self.window.refresh()


    def force_refresh(self):
        self.window.refresh()


    def update_window_size(self):
        self.height, self.width = self.window.getmaxyx()


    def get_new_windows_size(self):
        size = (self._nlines, self._ncols, self._begin_y, self._begin_x)
        new_size = [0, 0, 0, 0]

        for i, v in enumerate(size):
            if i & 1:
                s = self._screen.max_cols
            else:
                s = self._screen.max_rows

            if v < -1:
                new_size[i] = s + v
            else:
                new_size[i] = v

        return tuple(new_size)

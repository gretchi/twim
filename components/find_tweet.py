
import re
import curses
import logging

from .components_base import ComponentsBase
from const import const
from util import helper


class FindTweetWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)
        self.text = ""
        self.regex = None


    def draw(self):
        curses.cbreak()
        curses.curs_set(1)

        is_first = True

        while True:
            try:
                now_y, now_x = self.window.getyx()
                input_data = self.window.get_wch()
                input_data_type = type(input_data)
                key_cd = -1

                if type(input_data) is int:
                    logging.debug(f"Key input: (type: int, value: 0x{input_data:02X})")

                elif type(input_data) is str:
                    input_data_bytes = input_data.encode()
                    logging.debug(f"Key input: (type: int, value: {input_data_bytes})")

                    if input_data_bytes in (b"\x18", b"\x1B"):
                        # cancel
                        break

                    elif input_data_bytes == b"\n":
                        # Find
                        if is_first:
                            is_first = False
                        else:
                            try:
                                self.regex = re.compile(self.text)
                            except re.error as e:
                                logging.warning(e)
                                self.sys_mes = f"{e}"
                            break

                    elif input_data_bytes == b"\x7F":
                        logging.debug("<BS>")
                        if len(self.text) != 0:
                            last_char = self.text[-1]
                            last_size = helper.get_char_size(self.text[-1])
                            logging.debug(f"last char size: {last_size}")
                            if last_char not in ("\n", "\r", ""):
                                # self.window.delch(now_y, now_x - last_size)
                                pass

                        self.text = self.text[:-1]

                    else:
                        if not is_first:
                            self.text += input_data

                        is_first = False

                self.window.erase()
                self.window.box()
                self.window.border()
                self.window.addstr(0, 4, " Find ")


                footer = f"Find: Return, Cancel: ESC or C-x "

                self.window.addstr(self.height - 2, self.width - helper.get_text_width(footer) - 2, footer)

                logging.debug(helper.text_to_turnback_list(self.text, self.width - 4))

                self.window.addstr(2, 3, "Search word (Regex)")
                self.window.hline(3, 3, " ", self.width - 6, curses.A_UNDERLINE)
                self.window.addstr(3, 3, self.text, curses.A_UNDERLINE)
                # for i, line in enumerate(helper.text_to_turnback_list(self.text, self.width - 4)):
                #     self.window.addstr(1 + i, 2, line)
                #     if i >= self.height - 4:
                #         break

                self.window.refresh()

                logging.debug(f"inputing text: (width: {helper.get_text_width(self.text)}, text: \"{self.text}\")")
            except KeyboardInterrupt:
                logging.info("Input cancel.")
                break

        curses.nocbreak()
        curses.curs_set(0)

        self._screen.destroy_window(self.window_id)


import curses
import curses.textpad
import curses.ascii
import logging

from .components_base import ComponentsBase
from const import const
from util import helper


class TweetInputWindow(ComponentsBase):
    def __init__(self, parent, screen, nlines, ncols, begin_y, begin_x):
        super().__init__(parent, screen, nlines, ncols, begin_y, begin_x)
        self.text_pad = curses.textpad.Textbox(self.window, insert_mode=True)
        self.text = ""
        self.is_do_tweet = False
        self.in_reply_to_status_id = None
        self.screen_name = None

    def set_mention(self, in_reply_to_status_id, screen_name):
        self.in_reply_to_status_id = in_reply_to_status_id
        self.screen_name = f"@{screen_name}"
        self.text = self.screen_name + " "


    def draw(self):
        curses.cbreak()
        curses.curs_set(1)

        is_first = True
        auto_completion_mode = False
        candidate_screen_name_cursor = 0
        current_candidate_screen_name = ""

        while True:
            try:
                now_y, now_x = self.window.getyx()
                input_data = self.window.get_wch()
                input_data_type = type(input_data)
                key_cd = -1

                if type(input_data) is int:
                    logging.debug(f"Key input: (type: int, value: 0x{input_data:02X})")

                    if input_data == 0x102:
                        # Down Key
                        candidate_screen_name_cursor += 1

                    elif input_data == 0x103:
                        # Up Key
                        candidate_screen_name_cursor -= 1


                elif type(input_data) is str:
                    input_data_bytes = input_data.encode()
                    logging.debug(f"Key input: (type: str, value: {input_data_bytes})")

                    if input_data_bytes in (b"\x18", b"\x1B"):
                        # cancel
                        break

                    elif input_data_bytes == b"\x14":
                        # do tweet
                        self.is_do_tweet = True
                        break

                    elif len(self.text) == 0 and input_data_bytes == b"@":
                        # 入力補完
                        auto_completion_mode = True
                        self.text += input_data

                    elif input_data_bytes == b"\x7F":
                        logging.debug("<BS>")
                        if len(self.text) != 0:
                            last_char = self.text[-1]
                            last_size = helper.get_char_size(self.text[-1])
                            logging.debug(f"last char size: {last_size}")
                            if last_char not in ("\n", "\r", ""):
                                # self.window.delch(now_y, now_x - last_size)
                                pass

                        if self.screen_name is not None and len(self.text) <= len(self.screen_name):
                            # ユーザ名が削除された場合、メンションを取り消し
                            self.in_reply_to_status_id = None

                        self.text = self.text[:-1]

                        if len(self.text) == 0:
                            auto_completion_mode = False

                    elif auto_completion_mode and input_data_bytes == b"\n":
                        self.text += current_candidate_screen_name[len(self.text[1:].split(" ")[0]):] + " "
                        auto_completion_mode = False

                    else:
                        if not is_first:
                            self.text += input_data

                        is_first = False

                self.window.erase()
                self.window.box()
                self.window.border()
                self.window.addstr(0, 4, " Tweet body ")

                # ユーザ名入力補完
                if auto_completion_mode:
                    candidate_screen_names = self._parent.twitter.find_timeline_users(self.text[1:].split(" ")[0])
                    candidate_screen_names_length = len(candidate_screen_names)
                    if candidate_screen_names_length:
                        for row, candidate_screen_name in enumerate(candidate_screen_names[candidate_screen_name_cursor % candidate_screen_names_length:(candidate_screen_name_cursor % candidate_screen_names_length) + self.height - 5]):
                            logging.debug(candidate_screen_name)
                            if row == 0:
                                self.window.addnstr(row + 2, 3, candidate_screen_name, 40, curses.A_REVERSE)
                            else:
                                self.window.addnstr(row + 2, 3, candidate_screen_name, 40)
                        logging.debug(candidate_screen_names)
                        current_candidate_screen_name = candidate_screen_names[candidate_screen_name_cursor % candidate_screen_names_length]
                    else:
                        current_candidate_screen_name = ""


                if self.in_reply_to_status_id is not None:
                    reply_warning = f"Reply to {self.screen_name}"
                    self.window.addstr(self.height - 2, 2, reply_warning)

                footer = f"Send: C-t, Cancel: ESC or C-x ({len(self.text)}/140)"

                self.window.addstr(self.height - 2, self.width - helper.get_text_width(footer) - 2, footer)

                logging.debug(helper.text_to_turnback_list(self.text, self.width - 4))

                for i, line in enumerate(helper.text_to_turnback_list(self.text, self.width - 4)):
                    self.window.addstr(1 + i, 2, line)
                    if i >= self.height - 4:
                        break

                self.window.refresh()

                logging.debug(f"inputing text: (width: {helper.get_text_width(self.text)}, text: \"{self.text}\")")
            except KeyboardInterrupt:
                logging.info("Input cancel.")
                break


        curses.nocbreak()
        curses.curs_set(0)

        self._screen.destroy_window(self.window_id)

        logging.debug(f"is_do_tweet: {self.is_do_tweet}")


    def auto_completion(self, input):
        while True:
            logging.debug(self._parent.twitter.find_timeline_users(""))

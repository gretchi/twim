
import os
import json
import time
import datetime
import logging

from .twitter_api import TwitterAPI
from .tweet_object import Tweet
from util import helper
from const import const
from util import system_message

from .auth import Auth


FETCH_TWEETS_COUNT = 80

CONFIG_FILE_PATH = os.path.expanduser("~/.twim/access_token.json")


class Twitter:
    def __init__(self, consumer_api_key, consumer_api_secret, timezone):
        logging.debug(f"get_os_name(): {helper.get_os_name()}")
        logging.debug(f"CONFIG_FILE_PATH: {CONFIG_FILE_PATH}")

        access_token, access_token_secret = self.load_access_token(CONFIG_FILE_PATH)

        if access_token is None:
            logging.info("Authentication start.")
            auth = Auth(consumer_api_key, consumer_api_secret)
            access_token, access_token_secret = auth.auth_start()
            self.save_access_token(CONFIG_FILE_PATH, access_token, access_token_secret)


        self._api = TwitterAPI(consumer_api_key, consumer_api_secret, access_token, access_token_secret)

        self._cursor            = 0
        self.current_tweet_id   = 0
        self.current_user_id    = 0
        self.current_user_screen_name = ""
        self.api_remaining      = 0
        self.api_limit          = 0
        self.now_epoch          = 0
        self.update_at          = ""
        self.timeline_dict      = {}
        self.sorted_timeline    = []
        self._last_tweet_count  = 0
        self._since_id          = None
        self._timezone          = timezone
        self._update_now_epoch()
        self.next_update        = self.now_epoch + 2
        self._pageing_offset    = 0
        self.timeline_length    = 0
        self._last_jump_mode    = False
        self._timeline_users    = {}

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        value = min(value, self.timeline_length - 1)
        value = max(value, 0)

        self._cursor = value

        self.update_current_tweet_info()


    def _update_now_epoch(self):
        self.now_epoch = int(time.time())


    def update_timeline(self):
        wait = 60
        is_update = True

        self._update_now_epoch()

        if self.next_update >= self.now_epoch:
            return

        try:
            home_timeline = self._api.statuses_home_timeline(since_id=self._since_id, count=FETCH_TWEETS_COUNT)
        except Exception as e:
            wait = 5
            self.next_update = self.now_epoch + wait
            logging.error(e)
            system_message.set_mes(system_message.MES_LEVEL_ERROR, str(e))
            return

        self.api_remaining = home_timeline.api_remaining
        self.api_limit = home_timeline.api_limit

        if home_timeline.wait is not None:
            wait = home_timeline.wait
            is_update = False

        self.next_update = self.now_epoch + wait

        if is_update:
            if len(home_timeline.data) > 1:
                self._since_id = home_timeline.data[0]['id']

            tweet_count_diff = self.update_timeline_values(home_timeline.data)


            self.update_at = helper.strftime(datetime.datetime.now())

            logging.info(f"{tweet_count_diff} Tweet(s) acquired")

        system_message.set_mes(system_message.MES_LEVEL_INFO, "200 OK")
        return

    def toggle_favorite(self):
        current_tweet = self.get_current_tweet()
        if current_tweet is None:
            # ない
            system_message.set_mes(system_message.MES_LEVEL_WARN, "Is not exists Tweet.")
            return

        if not current_tweet.favorited:
            # ファボってない
            fav_res, sys_mes = self._api.favorites_create(self.current_tweet_id)
            if fav_res:
                sys_mes = "Added to favorites."
                current_tweet.favorited = True
            else:
                logging.error(sys_mes)
                system_message.set_mes(system_message.MES_LEVEL_ERROR, sys_mes)
                return

        else:
            # ファボってる
            fav_res, sys_mes = self._api.favorites_destroy(self.current_tweet_id)
            if fav_res:
                sys_mes = "Removed from favorites."
                current_tweet.favorited = False
            else:
                logging.error(sys_mes)
                system_message.set_mes(system_message.MES_LEVEL_ERROR, sys_mes)

        system_message.set_mes(system_message.MES_LEVEL_INFO, sys_mes)

    def retweet(self):
        current_tweet = self.get_current_tweet()
        if current_tweet is None:
            # ない
            system_message.set_mes(system_message.MES_LEVEL_WARN, "Is not exists Tweet.")
            return

        if current_tweet.retweeted:
            system_message.set_mes(system_message.MES_LEVEL_WARN, "This tweet is retweeted.")
            return

        status_code, data = self._api.statuses_retweet(current_tweet.tweet_id, trim_user="false")
        if status_code != 200:
            current_tweet.retweeted = True
            system_message.set_mes(system_message.MES_LEVEL_INFO, "retweeted.")
            # self.update_timeline_values(data)
        else:
            sys_mes =  data.get("error")
            logging.error(sys_mes)
            system_message.set_mes(system_message.MES_LEVEL_ERROR, sys_mes)



    def increment_cursor(self):
        self.cursor += 1

    def decrement_cursor(self):
        self.cursor -= 1

    def jump_to_prev_prev_user(self):
        i = self.cursor
        while True:
            i += 1
            seek_tweet = self.get_tweet_by_cursor(i)
            if seek_tweet is None:
                break

            if self.current_user_id == seek_tweet.user_id:
                self.cursor = i
                break


    def jump_to_next_same_user(self):
        i = self.cursor
        while True:
            i -= 1
            seek_tweet = self.get_tweet_by_cursor(i)
            if seek_tweet is None or (self.current_user_id != seek_tweet.user_id and i == 0):
                break

            if self.current_user_id == seek_tweet.user_id:
                self.cursor = i
                break


    def goto_find_prev(self, compiled_rergex_object):
        for i, v in enumerate(self.sorted_timeline[self.cursor::-1]):
            _, tweet = v
            if self.cursor == self.cursor - i:
                continue

            if compiled_rergex_object.search(tweet.text):
                logging.debug(f"Find match: {tweet.text}")
                self.cursor = self.cursor - i
                break
        else:
            system_message.set_mes(system_message.MES_LEVEL_WARN, "search hit TOP without match")

        return


    def goto_find_next(self, compiled_rergex_object):
        for i, v in enumerate(self.sorted_timeline[self.cursor:]):
            _, tweet = v
            if self.cursor == self.cursor + i:
                continue

            if compiled_rergex_object.search(tweet.text):
                logging.debug(f"Find match: {tweet.text}")
                self.cursor = i + self.cursor
                break
        else:
            system_message.set_mes(system_message.MES_LEVEL_WARN, "search hit BOTTOM without match")

        return


    def get_current_tweet(self):
        return self.get_tweet_by_cursor(self.cursor)


    def get_tweet_by_cursor(self, cursor):
        try:
            return self.sorted_timeline[cursor][1]
        except IndexError:
            return None


    def get_tweet_by_tweet_id(self, tweet_id):
        return self.timeline_dict.get(tweet_id)

    def update_current_tweet_info(self):
        current_tweet = self.get_current_tweet()
        if current_tweet is None:
            return

        self.current_tweet_id = current_tweet.tweet_id
        self.current_user_id = current_tweet.user_id
        self.current_user_screen_name = current_tweet.user_screen_name


    def update_unread(self):
        current_tweet = self.get_current_tweet()
        if current_tweet is None:
            return

        current_tweet.unread = False


    def jump_to_unread_tweet(self):
        is_exists_unread_tweet = False
        for i, v in enumerate(self.sorted_timeline):
            _, tweet = v
            if tweet.unread:
                self.cursor = i
                is_exists_unread_tweet = True

        if not is_exists_unread_tweet:
            self.cursor = 0

        self._last_jump_mode = True

        logging.debug("jump_to_unread_tweet()")


    def timeline_itar_pageing(self, nlines):
        offset = 0

        if self._last_jump_mode:
            offset = nlines - 3

        # logging.debug(f"offset: {offset}")


        if self._pageing_offset > self.cursor:
            self._pageing_offset = self.cursor - offset

        if self._pageing_offset < self.cursor - nlines + 2:
            self._pageing_offset = self.cursor - nlines + 2

        self._pageing_offset = max(0, self._pageing_offset)
        self._pageing_offset = min(self.timeline_length - nlines + 1, self._pageing_offset)


        start_id = self._pageing_offset
        end_id = self._pageing_offset + nlines

        for i, v in enumerate(self.sorted_timeline[start_id:end_id]):
            tweet_id, tweet = v
            yield tweet

        self._last_jump_mode = False

    def send_tweet(self, status, in_reply_to_status_id=None):
        status_code, data = self._api.statuses_update(status, in_reply_to_status_id=in_reply_to_status_id, trim_user="false")
        if status_code != 200:
            system_message.set_mes(system_message.MES_LEVEL_ERROR, data.get("error"))
            return

        system_message.set_mes(system_message.MES_LEVEL_INFO, "Successful tweet.")
        self.update_timeline_values(data)

        return

    def update_timeline_values(self, tweet_data):
        if type(tweet_data) is dict:
            timeline_data = [tweet_data]
        else:
            timeline_data = tweet_data

        for tweet in timeline_data:
            tweet_id = tweet['id']
            self.timeline_dict[tweet_id] = Tweet(tweet, self._timezone)
            self._timeline_users[tweet['user']['screen_name']] = None

        self.sorted_timeline = sorted(self.timeline_dict.items(), key=lambda x:x[0], reverse=True)
        self.timeline_length = len(self.sorted_timeline)
        tweet_count_diff = self.timeline_length - self._last_tweet_count

        self._last_tweet_count = self.timeline_length
        self.cursor += tweet_count_diff

        return tweet_count_diff


    def find_timeline_users(self, screen_name):
        match_list = []
        for k, v in sorted(self._timeline_users.items(), key=lambda x:x[0], reverse=False):
            screen_name_length = len(screen_name)

            if k[:screen_name_length] == screen_name:
                match_list.append(k)

        return match_list

    def jump_to_first(self):
        self.cursor = 0

    def jump_to_last(self):
        self.cursor = len(self.timeline_dict)

    def timeline_itar(self):
        for tweet_id, tweet in self.sorted_timeline:
            yield tweet


    def get_url_user_profile_by_tweet_id(self, tweet_id):
        tweet = self.get_tweet_by_tweet_id(tweet_id)

        return f"https://twitter.com/{tweet.user_screen_name}"


    def get_url_tweet_status_by_tweet_id(self, tweet_id):
        tweet = self.get_tweet_by_tweet_id(tweet_id)

        return f"https://twitter.com/{tweet.user_screen_name}/status/{tweet.id_str}"

    def save_access_token(self, path, access_token, access_token_secret):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)

        data = {
            "access_token": access_token
            , "access_token_secret": access_token_secret
        }

        with open(path, "w") as fh:
            json.dump(data, fh)

        logging.info(f"access token saved: {path}")

        return


    def load_access_token(self, path):
        if not os.path.exists(path):
            return None, None

        with open(path, "r") as fh:
            data = json.load(fh)

        return data.get("access_token"), data.get("access_token_secret")

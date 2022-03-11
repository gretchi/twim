
import datetime
import re
from pytz import timezone
from util import helper

class Tweet:
    def __init__(self, tweet, tz):
        # 内部パラメータ
        self.unread                     = True
        self.selecting                  = True


        # RT専用オブジェクト
        self.source                     = None
        self.origin_text                = None
        self.origin_user_name           = None
        self.origin_user_screen_name    = None
        self.origin_created_at_dt       = None
        self.origin_creates_at_str      = None

        # 通常オブジェクト
        self.tweet_id                   = tweet['id']
        self.id_str                     = tweet['id_str']
        self.is_retweet                 = bool(tweet.get('retweeted_status'))
        self.text                       = tweet['text']
        self.favorited                  = tweet['favorited']
        self.retweeted                  = tweet['retweeted']
        self.favorite_count             = tweet['favorite_count']
        self.retweet_count              = tweet['retweet_count']
        created_at                      = tweet['created_at']
        self.created_at_dt              = helper.non_locale_dependent_strptime(created_at).astimezone(timezone(tz))
        self.creates_at_str             = self.created_at_dt.strftime("%Y/%m/%d %H:%M:%S")
        self.user_id                    = tweet['user']['id']
        self.user_name                  = tweet['user']['name']
        self.user_screen_name           = tweet['user']['screen_name']
        self.following                  = tweet['user']['following']

        # 処理分け
        if self.is_retweet:
            # リツイート
            rt                              = tweet['retweeted_status']
            self.source                     = rt['source']
            self.source_name                = re.search(r'">(.+)</a>', self.source).group(1)
            self.origin_text                = rt['text']
            self.origin_user_name           = rt['user']['name']
            self.origin_user_screen_name    = rt['user']['screen_name']
            origin_created_at               = rt['created_at']
            self.origin_created_at_dt       = helper.non_locale_dependent_strptime(origin_created_at).astimezone(timezone(tz))
            self.origin_creates_at_str      = self.origin_created_at_dt.strftime("%Y/%m/%d %H:%M:%S")
        else:
            # 通常のツイート
            self.source                     = tweet['source']
            self.source_name                = re.search(r'">(.+)</a>', self.source).group(1)

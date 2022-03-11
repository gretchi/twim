
import json
import time

from requests_oauthlib import OAuth1Session


TOO_MENY_REQUESTS = 429

class TwitterAPI:
    def __init__(self, consumer_api_key, consumer_api_secret, access_token, access_token_secret):
        self._session = OAuth1Session(consumer_api_key, consumer_api_secret, access_token, access_token_secret)



    def statuses_home_timeline(self, **kwagrs):
        url = "https://api.twitter.com/1.1/statuses/home_timeline.json"

        params = {}
        params.update(kwagrs)

        resp = self._session.get(url, params=params)

        return Responce(resp)

    def statuses_retweet(self, tweet_id, **kwags):
        url = f"https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json"

        resp = self._session.post(url, params=kwags)
        decoded_data = json.loads(resp.text)

        return resp.status_code, decoded_data


    def favorites_create(self, tweet_id):
        url = "https://api.twitter.com/1.1/favorites/create.json"

        params = {
            "id": tweet_id
        }

        resp = self._session.post(url, params=params)
        decoded_data = json.loads(resp.text)

        if resp.status_code == 200:
            return True, None

        return False, decoded_data.get("error")


    def favorites_destroy(self, tweet_id):
        url = "https://api.twitter.com/1.1/favorites/destroy.json"

        params = {
            "id": tweet_id
        }

        resp = self._session.post(url, params=params)
        decoded_data = json.loads(resp.text)

        if resp.status_code == 200:
            return True, None

        return False, decoded_data.get("error")

    def statuses_update(self, status, **kwags):
        url = "https://api.twitter.com/1.1/statuses/update.json"

        params = {
            "status": status
        }

        params.update(kwags)

        resp = self._session.post(url, params=params)
        decoded_data = json.loads(resp.text)

        return resp.status_code, decoded_data




class Responce:
    def __init__(self, resp):
        data            = json.loads(resp.text)
        code            = resp.status_code
        api_remaining   = int(resp.headers["X-Rate-Limit-Remaining"])
        api_limit       = int(resp.headers["X-Rate-Limit-Limit"])
        api_reset       = int(resp.headers["X-Rate-Limit-Reset"])
        wait            = None

        if code == TOO_MENY_REQUESTS:
            wait = api_reset - int(time.time())

        self.data = data
        self.code = code
        self.wait = wait
        self.api_remaining = api_remaining
        self.api_limit = api_limit
        self.api_reset = api_reset

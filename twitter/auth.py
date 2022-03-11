
import requests
import time
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler

from requests_oauthlib import OAuth1Session

from util import helper

HOST = "127.0.0.1"
PORT = 37383
CALLBACK_URL = f"http://{HOST}:{PORT}/callback"

class Auth(object):
    def __init__(self, consumer_api_key, consumer_api_secret):
        self.consumer_api_key = consumer_api_key
        self.consumer_api_secret = consumer_api_secret
        self._session = OAuth1Session(self.consumer_api_key, self.consumer_api_secret)


    def auth_start(self):
        resource_owner_key, resource_owner_secret = self.oauth_request_token()

        authorization_url = self.oauth_authorize()

        helper.open_url(authorization_url)
        logging.info(authorization_url)

        oauth_response = self.listen()
        verifier = oauth_response.get('oauth_verifier')

        access_token, access_token_secret = self.oauth_access_token(resource_owner_key, resource_owner_secret, verifier)

        return access_token, access_token_secret

    def listen(self):
        redirect_response = None

        logging.info(f"HTTPServer listen start: {HOST}:{PORT}")
        with HTTPServer((HOST, PORT), CallBackHTTPServer) as httpd:
            httpd.handle_request()
            logging.debug(httpd.handle_insttance.path)
            redirect_response = httpd.handle_insttance.path


        oauth_response = self._session.parse_authorization_response(redirect_response)
        return oauth_response

    def oauth_access_token(self, resource_owner_key, resource_owner_secret, verifier):
        url = 'https://api.twitter.com/oauth/access_token'

        session = OAuth1Session(self.consumer_api_key,
                        client_secret=self.consumer_api_secret,
                        resource_owner_key=resource_owner_key,
                        resource_owner_secret=resource_owner_secret,
                        verifier=verifier)

        oauth_tokens = session.fetch_access_token(url)

        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')

        return access_token, access_token_secret



    def oauth_request_token(self):
        url = "https://api.twitter.com/oauth/request_token"

        fetch_response = self._session.fetch_request_token(url)

        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')

        return resource_owner_key, resource_owner_secret

    def oauth_authorize(self):
        url = "https://api.twitter.com/oauth/authorize"


        authorization_url = self._session.authorization_url(url)

        return authorization_url



class CallBackHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("""<!DOCTYPE html><html><head></head><body>Please close this tab.</body></html>""".encode())

        self.server.handle_insttance = self

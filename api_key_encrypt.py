#!/usr/bin/env python3

import sys

from twim import ck

CK_LENGTH = 25
CS_LENGTH = 50

if len(sys.argv) != 3:
    print("Usage: ./api_key_encrypt.py <CONSUMER_KEY> <CONSUMER_SECRET>")
    exit(1)

consumer_key = sys.argv[1]
consumer_secret = sys.argv[2]

if len(consumer_key) != CK_LENGTH:
    print("consumer key is invalid")
    exit(1)

if len(consumer_secret) != CS_LENGTH:
    print("consumer secret is invalid")
    exit(1)


# 暗号化
cipher_consumer_key = ck.encrypt(consumer_key.encode())
consumer_key_nonce = ck.get_latest_b64_nonce()

cipher_consumer_secret = ck.encrypt(consumer_secret.encode())
consumer_secret_nonce = ck.get_latest_b64_nonce()


# 結果出力
print("-" * 100)
print("Paste to ./api_key/__init__.py")
print("-" * 100)
print(f'CONSUMER_KEY = "{cipher_consumer_key}"')
print(f'CONSUMER_KEY_NONCE = "{consumer_key_nonce}"')
print(f'CONSUMER_SECRET = "{cipher_consumer_secret}"')
print(f'CONSUMER_SECRET_NONCE = "{consumer_secret_nonce}"')
print("-" * 100)

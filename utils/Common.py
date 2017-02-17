#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import binascii
import hashlib
import os


class Common:
    DATETIME_PATTERN_YYYYMMDD = '%Y-%m-%d'
    DATETIME_PATTERN_YYYYMMDDAA = '%Y-%m-%d %A'
    DATETIME_PATTERN_HHMMSS = '%H:%M:%S'
    DATETIME_PATTERN_YYYYMMDDHHMMSS = DATETIME_PATTERN_YYYYMMDDAA + ' ' + DATETIME_PATTERN_HHMMSS

    def __init__(self):
        pass

    @staticmethod
    def format_datetime(dt, pattern=DATETIME_PATTERN_YYYYMMDDHHMMSS):
        """
        :type pattern: str
        :type dt: datetime
        """
        return time.strftime(pattern, dt.timetuple())

    @staticmethod
    def format_date(dt, pattern=DATETIME_PATTERN_YYYYMMDDAA):
        """
        :type pattern: str
        :type dt: datetime
        """
        return time.strftime(pattern, dt.timetuple())

    @staticmethod
    def format_time(dt, pattern=DATETIME_PATTERN_HHMMSS):
        """
        :type pattern: str
        :type dt: datetime
        """
        return time.strftime(pattern, dt.timetuple())

    @staticmethod
    def get_today():
        """
        :rtype: datetime
        """
        return datetime.today()

    @staticmethod
    def get_tomorrow():
        """
        :rtype: datetime
        """
        return Common.get_datetime_with_interval(1)

    @staticmethod
    def get_day_after_tomorrow():
        """
        :rtype: datetime
        """
        return Common.get_datetime_with_interval(2)

    @staticmethod
    def get_datetime_with_interval(days):
        """
        :rtype: datetime
        """
        return datetime.today() + timedelta(days=days)

    @staticmethod
    def encrypt_content_by_aes(content, secret):
        encryptor = AES.new(secret)
        encrypted = encryptor.encrypt(content)
        return binascii.hexlify(encrypted)

    @staticmethod
    def decrypt_content_by_aes(encrypted, secret):
        raw = binascii.unhexlify(encrypted)
        decryptor = AES.new(secret)
        decrypted = decryptor.decrypt(raw)
        return decrypted

    @staticmethod
    def md5(content):
        content = '' if content is None else content
        return hashlib.md5(content).hexdigest()

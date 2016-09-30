#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class JsonReader:
    def __init__(self):
        pass

    @staticmethod
    def read(path):
        with open(path, 'r') as f:
            return json.load(f)

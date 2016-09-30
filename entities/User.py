#!/usr/bin/env python
# -*- coding: utf-8 -*-


class User:
    def __init__(self, name, student_id, username, password, phone, user_type):
        self.name = name
        self.student_id = student_id
        self.username = username
        self.password = password
        self.phone = phone
        self.user_type = user_type

    def get_login_params(self):
        return {
            'redirect': 'NO',
            'userName': self.username,
            'password': self.password,
            'x': 0,
            'y': 0
        }

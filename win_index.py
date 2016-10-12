#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plugins.BackendService import BackendService
import win32serviceutil

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BackendService)

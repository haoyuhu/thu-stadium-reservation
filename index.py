#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plugins.MasterScheduler import MasterScheduler

REMOTE_MODE = True

master_scheduler = MasterScheduler(REMOTE_MODE)


def start_scheduler():
    master_scheduler.start()


def stop_scheduler():
    master_scheduler.stop()


if __name__ == "__main__":
    start_scheduler()

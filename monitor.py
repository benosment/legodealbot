#! /usr/bin/env python3

import subprocess
import os
from legodealbot import send_email
import logging


PROCESS_NAME = 'legodealbot.py'
VENV_PATH = '/home/pi/legodealbot/venv/bin/python'


def process_is_down(process_name):
    all_processes = subprocess.check_output("ps -ef".split()).splitlines()
    for process in all_processes:
        if process_name in str(process):
            return False
    return True


def send_respawn_email(cmd):
    email_title = 'Respawning %s' % PROCESS_NAME
    email_body = 'Respawning process %s' % cmd
    send_email(email_title, email_body)


def respawn():
    dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    command = "nohup %s %s/%s" % (VENV_PATH, dir, PROCESS_NAME)
    logging.debug('Respawning process %s', command)
    send_respawn_email(command)
    subprocess.run(command.split())


if __name__ == "__main__":
    if process_is_down(PROCESS_NAME):
        print("respawning process %s" % PROCESS_NAME)
        respawn()
    else:
        print("%s is up" % PROCESS_NAME)

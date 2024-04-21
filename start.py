#!/usr/bin/env python3

import importlib
import os
import sys
import time

# Entry point for websitebackup
start_text = """
========================
  Welcome to website
    Backup/Restore
========================
    Backup  - [b]
    Restore - [r]
------------------------
     cancel - [x]
"""


def startup():
    os.system("clear")
    print(start_text)
    cmd = input("What would you like to to?: ").lower()
    os.system("clear")
    return cmd


while True:
    cmd = startup()

    if cmd == "x":
        print("Program stopping!")
        time.sleep(1)
        break

    elif cmd == "b":
        if "backup" not in sys.modules:
            import backup as backup
        else:
            importlib.reload(backup)

    elif cmd == "r":
        if "restore" not in sys.modules:
            import restore
        else:
            importlib.reload(restore)

    else:
        os.system("clear")
        print("no valid command")
        time.sleep(2)

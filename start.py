#!/usr/bin/env python3

import importlib
import os
import sys
import time

# Entry point for websitebackup
start_text = """
========================
Willkommen zum Website
    Backup/Restore
========================
    Backup  - [b]
    Restore - [r]
------------------------
  abbrechen - [x]
"""


def startup():
    os.system("clear")
    print(start_text)
    cmd = input("Was wollen Sie tun?: ").lower()
    os.system("clear")
    return cmd


while True:
    cmd = startup()

    if cmd == "x":
        print("Das Programm wird beendet!")
        time.sleep(1)
        break

    elif cmd == "b":
        if "jbackup" not in sys.modules:
            import jbackup
        else:
            importlib.reload(jbackup)

    elif cmd == "r":
        if "jrestore" not in sys.modules:
            import jrestore
        else:
            importlib.reload(jrestore)

    else:
        os.system("clear")
        print("kein gültiges Kommando")
        time.sleep(2)

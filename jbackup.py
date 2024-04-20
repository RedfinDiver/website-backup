#!/usr/bin/env python3

import os
import time
from configparser import ConfigParser, ExtendedInterpolation
import paramiko


class JBackup:
    """Backup of a Joomla! install via ssh

    This needs the backup_on_server.py script on the webserver
    """

    def __init__(self, host, username, key_file_path):
        """Create all necessary variables"""
        self.host = host
        self.username = username
        self.key_file_path = key_file_path

    def connect_to_server(self):
        """Establish a ssh connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                self.host, username=self.username, key_filename=self.key_file_path
            )
            print(f"Verbindung zu {self.host} erfolgreich!")
        except:
            print(f"Verbindung mit {self.host} gescheitert!")
            print("Bitte nochmal versuchen!")

        return ssh

    @staticmethod
    def build_command(cfg, cmd):
        bk_cmd = (
            f"python3 {cfg['default']['backup_file']} "
            f"{cfg['default']['backup_base']}{cmd} "
            f"{cfg['default']['backup_target_base']}{cmd} "
            f"{cfg[cmd]['dbuser']} {cfg[cmd]['dbpass']} {cfg[cmd]['db']} "
        )
        return bk_cmd

def print_success(value, cmd):
    if value == 0:
        print(f"Backuperstellung für '{cmd}' erfolgreich.")
    else:
        print(f"Fehler bei der Backuperstellung für '{cmd}'")

###############################################################################
##################### Script section of this file #############################
###############################################################################

cfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
cfg.read("backup.cfg")

backup_text = """
=====================================
          Website BACKUP
=====================================
 taekwondo-uttendorf.at - [uttendorf]
taekwondo-innviertel.at - [tgi]
       taekwondo-ooe.at - [ooetdv]
  magique-cosmetique.at - [magcos]
-------------------------------------
    alle oben stehenden - [a]
              abbrechen - [x]
-------------------------------------
"""

bk = JBackup(
    cfg["default"]["host"], cfg["default"]["user"], cfg["default"]["ssh_key_file"]
)

ssh = bk.connect_to_server()

while True:
    os.system("clear")
    print(backup_text)
    cmd = input("Wählen Sie eine Option: ").lower()
    os.system("clear")

    # back to entry script
    if cmd == "x":
        ssh.close()
        print(f"Verbindung zu '{cfg['default']['host']}' geschlossen!")
        time.sleep(2)
        break
    # single backup
    elif not cmd == "a" and cmd in cfg and not cmd == "default":
        os.system("clear")
        print("Auswahl: ", cmd)
        stdin, stdout, stderr = ssh.exec_command(bk.build_command(cfg, cmd))
        exit_status = stdout.channel.recv_exit_status()
        print_success(exit_status, cmd)
        time.sleep(3)
    # backup of all websites
    elif cmd == "a":
        print("Auswahl: ", cmd)
        for section in cfg.sections():
            if not section == "default":
                stdin, stdout, stderr = ssh.exec_command(bk.build_command(cfg, section))
                exit_status = stdout.channel.recv_exit_status()
                print_success(exit_status, section)
                time.sleep(3)
    # no valid command
    else:
        os.system("clear")
        print(f'"{cmd}" ist keine gültige Auswahl!')
        time.sleep(2)


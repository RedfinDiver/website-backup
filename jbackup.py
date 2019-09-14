#!/usr/bin/env python3

import paramiko


class JBackup:
    """Backup of a Joomla! installtion via ssh

    This needs the backup.py script on the webserver
    """

    def __init__(self, host, username, key_file_path):
        """Establish a ssh connection"""
        self.host = host
        self.username = username
        self.key_file_path = key_file_path

    def connect_to_server(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            ssh.connect(self.host, self.username, self.key_file_path)
            print(f"Verbindung zu {self.host} erfolgreich!")
        except:
            print(f"Verbindung mit {self.host} gescheitert!")
            print("Bitte nochmal versuchen!")

        return ssh

#!/usr/bin/env python3

import os
import re
import shutil
import time
import webbrowser
from configparser import ConfigParser, ExtendedInterpolation

import mysql.connector


class JRestore:
    """Handles restore of a Joomla! zip-Backup

    This modules handles copy, unzipping and rewriting config file for a
    Joomla! Backup recovery on a local development machine
    Args:
        source (str): Filepath to backup folder
        target (str): Folder on local machine
    """

    def __init__(self, source, target):
        self.zip_name = self.get_newest_file(source)
        self.file = os.path.join(source, self.zip_name)
        self.restore_name = os.path.basename(os.path.normpath(source))
        self.restore_folder = target
        self.replaces = {
            "$db": f"'{self.restore_name}'",
            "$log_path": "'" + os.path.join(self.restore_folder, "logs") + "'",
            "$password": "''",
            "$user": "'root'",
            "$host": "'mysql'",
        }

    def copy_and_unzip(self):
        """Copy and unzip the backup archive"""
        file = os.path.join(self.restore_folder, self.zip_name)
        if os.path.isdir(self.restore_folder):
            shutil.rmtree(self.restore_folder, ignore_errors=False)
        os.makedirs(self.restore_folder)

        shutil.copy2(self.file, self.restore_folder)
        shutil.unpack_archive(file, self.restore_folder, "zip")
        os.remove(file)
        print("Archivdatei wurde entpackt...")

    def restore_database(self):
        """Restore the database on local machine"""
        db = mysql.connector.connect(host="127.0.0.1", user="root", passwd="")
        c = db.cursor()

        try:
            c.execute(f"CREATE DATABASE `{self.restore_name}`")
        except (mysql.connector.errors.DatabaseError) as e:
            error = e.errno
            if error == 1007:
                c.execute(f"DROP DATABASE `{self.restore_name}`")
                c.execute(f"CREATE DATABASE `{self.restore_name}`")

        sql_file = os.path.join(self.restore_folder, self.restore_name + ".sql")
        os.system(
            f"cat {sql_file} | docker exec -i devilbox_mysql_1 "
            f"/usr/bin/mysql -u root {self.restore_name}"
        )

        print("Datenbank wurde hergestellt...")

    @staticmethod
    def get_newest_file(path):
        """Returns path of newest file in a given filepath"""
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        newest_file = list(sorted(os.listdir(path), key=mtime))[-1]
        print(f'Backup wird hergestellt aus Archivdatei "{newest_file}"...')
        return newest_file

    def make_config_file(self):
        """Rewrite a Joomla config file for local development"""
        config_file = os.path.join(self.restore_folder, "configuration.php")
        with open(config_file, "r") as conf:
            lines = conf.readlines()

        new_config = {}
        for line in lines:
            if re.search("public", line):
                variable, value = line.strip()[:-1].replace("public ", "").split(" = ")
                new_config.update({variable: value})
        new_config.update(self.replaces)

        os.remove(config_file)
        with open(config_file, "w") as file:
            file.write("<?php\nclass JConfig {\n")
            for variable, value in new_config.items():
                file.write(f"\tpublic {variable} = {value};\n")
            file.write("}")
        print("Konfigurationsdatei wurde angepasst...")

    def open_target(self):
        """Open the restored website in firefox"""
        website = f"http://{self.restore_name}.local"
        print(f"Öffne lokale Website {website} (Frontend und Backend)...")
        webbrowser.open(website)
        webbrowser.open(website + "/administrator")

    def restore(self):
        """Wrapper for all methods of JRestore class"""
        self.copy_and_unzip()
        self.restore_database()
        self.make_config_file()
        self.open_target()
        print("Website erfolgreich wieder hergestellt!")


###############################################################################
##################### Script section of this file #############################
###############################################################################


def source_paths(cfg, section_to_parse):
    """Prepare paths from configuration object"""
    paths = {}
    for key in cfg[section_to_parse]:
        path = {key: cfg[section_to_parse][key]}
        paths.update(path)
    return paths


cfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
cfg.read("restore.cfg")

text = """
=====================================
    Website Wiederherstellung
=====================================
 taekwondo-uttendorf.at - [uttendorf]
taekwondo-innviertel.at - [tgi]
       taekwondo-ooe.at - [ooetdv]
   magique-cometique.at - [magcos]
-------------------------------------
    alle oben stehenden - [a]
              abbrechen - [x]
-------------------------------------
"""

restore_source_paths = source_paths(cfg, "restore_source_paths")
restore_target_paths = source_paths(cfg, "restore_target_paths")

while True:
    os.system("clear")
    print(text)
    cmd = input("Wählen Sie eine Option: ").lower()
    os.system("clear")

    # back to entry script
    if cmd == "x":
        break
    # valid single restore command
    elif not cmd == "alle" and cmd in restore_source_paths:
        os.system("clear")
        print("Auswahl: ", cmd)
        source = restore_source_paths[cmd]
        target = restore_target_paths[cmd]
        bk = JRestore(source, target)
        bk.restore()
        time.sleep(2)
    # restore everything
    elif cmd == "a":
        os.system("clear")
        print("Wiederherstellung aller Websites...")
        for key, source in restore_source_paths.items():
            os.system("clear")
            target = restore_target_paths[key]
            bk = JRestore(source, target)
            bk.restore()
            time.sleep(2)
    # no valid command, try again
    else:
        os.system("clear")
        print("kein gültiges Kommando")
        time.sleep(2)

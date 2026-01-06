#!/usr/bin/env python3

import os
import re
import shutil
import time
import webbrowser
from configparser import ConfigParser, ExtendedInterpolation
import yaml
import subprocess


class Restore:
    """Handles restore of a Joomla! zip-Backup

    This modules handles copy, unzipping and rewriting config file for a
    Joomla! Backup recovery on a local development machine
    Args:
        source (str): Filepath to backup folder
        target (str): Folder on local machine
        php    (str): php version to restore to
        db     (str): database version to restore to
    """

    def __init__(self, source, target, php, db):
        self.zip_name = self.get_newest_file(source)
        self.file = os.path.join(source, self.zip_name)
        self.restore_name = os.path.basename(os.path.normpath(source))
        self.restore_folder = target
        self.replaces = {
            "$db": f"'{self.restore_name}'",
            "$log_path": "'/app/www/logs'",
            "$tmp_path": "'/app/www/tmp'",
            "$password": "'admin'",
            "$user": "'admin'",
            "$host": "'database'",
        }
        self.php = php
        self.db  = db

    def copy_and_unzip(self):
        """Copy and unzip the backup archive"""

        # if there is a directory, destroy lando app and wipe it
        if os.path.isdir(self.restore_folder):
            os.chdir(self.restore_folder)
            os.system(f"lando destroy -y")
            os.system(f"lando poweroff")
            shutil.rmtree(self.restore_folder, ignore_errors=False)

        # make the restore directory
        os.makedirs(self.restore_folder)

        # copy over the zip file, unpack and remove it
        file = os.path.join(self.restore_folder, self.zip_name)
        shutil.copy2(self.file, self.restore_folder)
        shutil.unpack_archive(file, self.restore_folder, "zip")
        os.remove(file)
        print("Archive was unpacked, lando file was created!")
        time.sleep(2)

    def create_landofile(self):
        """ creates a landofile """
        os.chdir(os.path.dirname(__file__))
        with open('lando.yml', 'r') as file:
            data = yaml.safe_load(file)

        data['name'] = self.restore_name
        data['services']['database']['creds']['database'] = self.restore_name
        data['services']['database']['type'] = self.db
        data['proxy']['appserver'] = [self.restore_name + '.local']
        data['config']['php'] = self.php

        lando_file = os.path.join(self.restore_folder, '.lando.yml')
        with open(lando_file, 'w') as file:
            yaml.dump(data, file)

    def start_lando(self):
        """Starting lando app"""
        os.chdir(self.restore_folder)
        subprocess.run(["lando", "destroy", "-y"])
        subprocess.run(["lando", "poweroff"])
        subprocess.run(["lando", "start"])
        print("Lando app started!")
        time.sleep(2)

    def import_database(self):
        """Restore the database on lando setup"""
        sql_file = self.restore_name + ".sql"

        os.chdir(self.restore_folder)

        # Quick fix, delete first line of mariadb dump
        # see https://mariadb.org/mariadb-dump-file-compatibility-change/

        with open(sql_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(sql_file, "w", encoding="utf-8") as file:
            file.writelines(lines[1:])

        os.system(f"lando db-import {sql_file}")

        print("Database was imported in lando app!")

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
        website = f"https://{self.restore_name}.local"
        print(f"Öffne lokale Website {website} (Frontend und Backend)...")
        webbrowser.open(website)
        webbrowser.open(website + "/administrator")

    def restore(self):
        """Wrapper for all methods of JRestore class"""
        self.copy_and_unzip()
        self.make_config_file()
        self.create_landofile()
        self.start_lando()
        self.import_database()
        self.open_target()
        print("Website erfolgreich wieder hergestellt!")


###############################################################################
##################### Script section of this file #############################
###############################################################################

def get_config(cfg, section_to_parse):
        """Prepare config params from configuration object"""
        params = {}
        for key in cfg[section_to_parse]:
            param = {key: cfg[section_to_parse][key]}
            params.update(param)
        return params

cfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
cfg.read("restore.cfg")

restore_text = """
=====================================
        Website local RESTORE
=====================================
 taekwondo-uttendorf.at - [uttendorf]
taekwondo-innviertel.at - [tgi]
       taekwondo-ooe.at - [ooetdv]
  magique-cosmetique.at - [magcos]
-------------------------------------
                 cancel - [x]
-------------------------------------
"""

restore_source_paths = get_config(cfg, "restore_source_paths")
restore_target_paths = get_config(cfg, "restore_target_paths")
restore_phpversion   = get_config(cfg, "restore_phpversion")
restore_dbversion    = get_config(cfg, "restore_dbversion")

while True:
    os.system("clear")
    print(restore_text)
    cmd = input("Choose an option: ").lower()
    os.system("clear")

    # back to entry script
    if cmd == "x":
        break
    # valid single restore command
    elif not cmd == "x" and cmd in restore_source_paths:
        os.system("clear")
        print("Selection: ", cmd)
        source = restore_source_paths[cmd]
        target = restore_target_paths[cmd]
        php    = restore_phpversion[cmd]
        db     = restore_dbversion[cmd]
        bk = Restore(source, target, php, db)
        bk.restore()
        time.sleep(2)
    # no valid command, try again
    else:
        os.system("clear")
        print("no valid command")
        time.sleep(2)

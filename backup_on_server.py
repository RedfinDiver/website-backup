#!/usr/bin/env python3

""" Backup file to put on server

This file should be placed on the server. It is either triggerd by a cron job
or via a ssh session.
"""

import argparse
import os
import shutil
import tempfile
from datetime import datetime as time

# parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("folder_to_backup", help="The folder to backup")
parser.add_argument("folder_for_backup", help="The folder to store the backup")
parser.add_argument("db_user", help="Name of database user")
parser.add_argument("db_password", help="Password for the database")
parser.add_argument("db_name", help="Name of the database")
args = parser.parse_args()

# preferences
archives_to_keep = 12

# all paths and file names needed are specified here
bak_name = os.path.basename(args.folder_to_backup)
zip_file_name = bak_name + "_" + time.now().strftime("%Y-%m-%d")
zip_file = os.path.join(args.folder_for_backup, zip_file_name)

# check for archive folder
if not os.path.exists(args.folder_for_backup):
    os.makedirs(args.folder_for_backup)

# zipping of folders and files into tempfile
with tempfile.TemporaryDirectory() as working_dir:
    wd = os.path.join(working_dir, bak_name)
    sql = os.path.join(wd, bak_name + ".sql")
    shutil.copytree(args.folder_to_backup, wd)

    dump_cmd = "mysqldump -u {dbu} -p{dbp} {dbn} > {sf}".format(
        dbu=args.db_user, dbp=args.db_password, dbn=args.db_name, sf=sql
    )
    os.system(dump_cmd)
    shutil.make_archive(zip_file, "zip", wd)

# define function for housekeeping
def delete_old_files(path, files_to_keep):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    list_sorted = list(sorted(os.listdir(path), key=mtime))
    if len(list_sorted) > files_to_keep:
        del_list = list_sorted[0 : (len(list_sorted) - files_to_keep)]
        for file in del_list:
            os.remove(path + "/" + file)


# housekeeping on webserver
delete_old_files(args.folder_for_backup, archives_to_keep)

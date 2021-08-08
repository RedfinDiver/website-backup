# website-backup
My scripts to backup and restore of maintained websites with python

## Preparations
- Place the file backup_on_server.py somewhere on the server
- To use the pipenv app locally, rename the backup_example.cfg to backup.cfg, Rename restore_example.cfg to restore.cfg and change the entries in that files to your needs

## Backup

### Use as Cron job or directly on ssh session

The file backup_on_server.py can be triggerd by a cron job via a ssh session or manually in a ssh session. The arguments to the script are:
```
serverprompt> pyhton3 backup_on_server.py folder_source folder_target db_user db_password db_name dbx_token
```

So the command for a cron job could be something like that:
```
ssh webserver "cd /folder/of/sript/; python3 ./backup_on_server.py /folder/source /folder/target backupuser secretpw db_name ljjdsjojdefjxdfdf" 
```
Make sure to have the `webserver` configured in your .ssh!

### Pipenv app
To use the python app, create the pipenv:
```
localprompt> pipenv shell
```
The app is created and you can run the programm:
```
pipenv-prompt> python start.py
```

## Restore
Currently only local restores are supported. To restore run the pipenv app locally as described before. Make sure to have php, apache2 and mysql running on `localhost`.

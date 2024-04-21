# website-backup
My scripts to backup and restore my maintained websites with python on a lando setup. As this is a very customized toolset it is not very likely it will give anybody else some benefits. So this is more or less documentation for myself ;-)

## Preparations
- Place the file serverfile.py somewhere on the server
- To use the pipenv app locally, rename the backup_example.cfg to backup.cfg, rename restore_example.cfg to restore.cfg and change the entries in that files to your needs
- In order to restore websites locally make shure that [lando](https://lando.dev/) is installed on your system

## Backup

### Use as Cron job or directly on ssh session

The file serverfile.py can be triggerd by a cron job via a ssh session or manually in a ssh session. The arguments to the script are:
```
serverprompt> pyhton3 serverfile.py folder_source folder_target db_user db_password db_name dbx_token
```

So the command for a cron job could be something like that:
```
ssh webserver "cd /folder/of/sript/; python3 ./serverfile.py /folder/source /folder/target backupuser secretpw db_name ljjdsjojdefjxdfdf" 
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
Currently only local restores are supported. To restore run the pipenv app locally as described before. The selected websites are restored using a lando app. For this purpose a .lando.yml file is created and the lando app is then started.

Be aware that only one website at a time can be restored and started. This is intentionally for a lando enviroment. One app for each project!

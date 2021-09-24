# rsync_files_from_digitalocean

## description

Tool to automate running a rsync command on a subset of digital ocean droplets


## usage

```
usage: cli.py [-h] [--log-to-file-path LOG_TO_FILE_PATH] [--verbose] [--no-stdout] [--dry-run] --digital-ocean-api-key DIGITAL_OCEAN_API_KEY [--droplet-name-regex DROPLET_NAME_REGEX]
              --rsync-binary RSYNC_BINARY --rsync-username RSYNC_USERNAME [--rsync-filter RSYNC_FILTER] [--remove-source-files] --droplet-source-folder DROPLET_SOURCE_FOLDER
              --local-destination-folder LOCAL_DESTINATION_FOLDER

run rsync on a subset of digital ocean serverse

optional arguments:
  -h, --help            show this help message and exit
  --log-to-file-path LOG_TO_FILE_PATH
                        log to the specified file
  --verbose             Increase logging verbosity
  --no-stdout           if true, will not log to stdout
  --dry-run             if specified, don't actually perform any action
  --digital-ocean-api-key DIGITAL_OCEAN_API_KEY
                        the DigitalOcean API key
  --droplet-name-regex DROPLET_NAME_REGEX
                        a regular expression to check the droplet names against, if the name matches, we will download files from this droplet
  --rsync-binary RSYNC_BINARY
                        path to the rsync binary
  --rsync-username RSYNC_USERNAME
                        rsync ssh username
  --rsync-filter RSYNC_FILTER
                        a filter to provide to rsync, can be specified multiple times
  --remove-source-files
                        if specified, we will remove the source files when running rsync
  --droplet-source-folder DROPLET_SOURCE_FOLDER
                        the folder on the remote side that we will be rsyncing from
  --local-destination-folder LOCAL_DESTINATION_FOLDER
                        the local folder to store the files in

Copyright 2021-09-02 - Mark Grandi
```
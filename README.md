# Subfinder

This script scans a directory and download the subtitles for each movie found using open subtitles API.
It uses a config file (_config.py_) to determine the language to search, and the open subtitles credentials to use to connect the API.

## Requirements

Python 3

## Install

```
git clone git@github.com:nberard/subfinder.git 
git submodule update --init
cp config.py.dist config.py
```

Change _config.py_ with your open subtitles credentials, adapt it to your needs and run

```
./synchro_subtitles.py <pathToValidDirectory>
```

## Docker 

```
cp .env.dist .env 
```
and change it to your needs
```
docker build -t subfinder [--build-arg uid=<the_uid_to_use_for_files_creation>] . 
docker run --name subfinder -d --env-file=.env -v [your_directory_to_scan]:/data subfinder
```
### Reset exclude list

If the script cannot find the substitles, it will add the video file to an exclude list.
The exclude list is stored inside data folder and so you can reset it by deleting the file _data/exclude.lst_
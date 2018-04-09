# Subfinder

This script scans a directory and download the subtitles for each movie found using open subtitles API.
It uses a config file (_config.py_) to determine the language to search, and the open subtitles credentials to use to connect the API.

## Requirements

Python 3 and Pip

## Install

```
git clone git@github.com:nberard/subfinder.git 
pip3 install -r requirements.txt
git submodule update --init
cp config.py.dist config.py
```

Change _config.py_ with your open subtitles credentials, adapt it to your needs and run

```
./synchro_subtitles.py <pathToValidDirectory>
```

### Reset exclude list

If the script cannot find the substitles, it will add the video file to an exclude list.
The exclude list is stored inside data folder and so you can reset it by deleting the file _data/exclude.lst_
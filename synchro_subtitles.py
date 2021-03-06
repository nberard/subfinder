#!/usr/local/bin/python3
# -*-coding:utf-8 -*

import datetime
import gzip
import os
import pickle
import sys
from http.client import ResponseNotReady
from time import sleep
from urllib import request
from xmlrpc.client import ProtocolError

import config
from python_opensubtitles.pythonopensubtitles.opensubtitles import OpenSubtitles
from python_opensubtitles.pythonopensubtitles.utils import File

valid_extensions = [".avi", ".mkv", ".mpeg", ".mpg", ".mp4", ".m4v"]
subtitles_extension = ".srt"
exclude_list_filename = "data/exclude.lst"
base_dir = os.path.dirname(__file__)


def save_exclude_list(exclude_list):
    with open(exclude_list_filename, 'wb') as fichier:
        depickler = pickle.Pickler(fichier)
        depickler.dump(exclude_list)


def get_exclude_list():
    exclude_list = []
    if os.path.exists(exclude_list_filename):
        with open(exclude_list_filename, 'rb') as fichier:
            depickler = pickle.Unpickler(fichier)
            exclude_list = depickler.load()
    return exclude_list


def subtitle_exists(path, file, extension):
    return os.path.exists(os.path.join(path, file.replace(extension, subtitles_extension)))


def is_valid_file(path, file):
    for valid_extension in valid_extensions:
        if file.endswith(valid_extension):
            return not subtitle_exists(path, file, valid_extension)
    return False


def list_valid_files_in_directory(path):
    files = os.listdir(path)
    dir_content = []
    for entry in files:
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            dir_content += list_valid_files_in_directory(entry_path)
        else:
            if is_valid_file(path, entry):
                dir_content.append(entry_path)
    return dir_content


def download_and_unzip_file(subtitles_url, video_to_get_sub):
    filename = os.path.basename(video_to_get_sub)
    dirname = os.path.dirname(video_to_get_sub)
    subtitles_filename = filename[:-4] + subtitles_extension
    gz_file = subtitles_filename + ".gz"
    handle = request.urlopen(subtitles_url).read()
    with open(gz_file, 'wb') as outfile:
        outfile.write(handle)
    with gzip.open(gz_file, 'rb') as gz_file_handler:
        with open(os.path.join(dirname, subtitles_filename), 'wb') as outfile:
            outfile.write(gz_file_handler.read())
    os.remove(gz_file)


def call_and_retry(function, *args):
    max_retries = 5
    sleep_time = 3
    retries = 0
    result = None
    while not result and retries < max_retries:
        try:
            result = function(*args)
            break
        except (ProtocolError, ResponseNotReady) as e:
            print('Too many requests, retrying in {}s'.format(sleep_time))
            print(e)
            sleep(sleep_time)
            retries += 1
    if not result and retries == max_retries:
        raise Exception('too many retries for request {}{}'.format(function.__name__, args))
    return result


if not os.path.exists("config.py"):
    print("Please create config.py file by copying config.py.dist and adapt it to your needs", file=sys.stderr)
    exit(1)

if len(sys.argv) != 2 or (not os.path.isdir(sys.argv[1]) and not os.path.isfile(sys.argv[1])):
    print("Usage: ./synchro_subtitles.py <validDirectoryOrFile>", file=sys.stderr)
    exit(2)

subtitles_config = config.open_subtitles

if not ("language" in subtitles_config and "login" in subtitles_config and "password" in subtitles_config):
    print("Invalid configuration (see config.py.dist for example)", file=sys.stderr)
    exit(3)

if "user_agent" in subtitles_config:
    os.environ["OS_USER_AGENT"] = subtitles_config['user_agent']

path = sys.argv[1]
valid_files_in_directory = list_valid_files_in_directory(path) if os.path.isdir(path) else [path]
exclude_list = get_exclude_list()
files_not_excluded = [file for file in valid_files_in_directory if file not in exclude_list]
if files_not_excluded:
    open_sub = OpenSubtitles()
    token = call_and_retry(open_sub.login, subtitles_config['login'], subtitles_config['password'])
    if token is None:
        print("Invalid open subtitles credentials (see config.py)", file=sys.stderr)
        exit(4)
    for video_to_get_sub in files_not_excluded:
        sub_file = File(video_to_get_sub)
        data = call_and_retry(open_sub.search_subtitles, [
            {'sublanguageid': subtitles_config['language'], 'moviehash': sub_file.get_hash(),
             'moviebytesize': sub_file.size}
        ])
        try:
            subtitles_file = data[0]["SubDownloadLink"]
            download_and_unzip_file(subtitles_file, video_to_get_sub)
            print(datetime.datetime.now().isoformat(), " --- subtitle found for ", video_to_get_sub)
        except IndexError as e:
            print(datetime.datetime.now().isoformat(), " --- /!\ no subtitles found for ", video_to_get_sub,
                  file=sys.stderr)
            exclude_list.append(video_to_get_sub)

    save_exclude_list(exclude_list)

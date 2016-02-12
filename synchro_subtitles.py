#!/usr/bin/python3
# -*-coding:utf-8 -*

import os
import sys
import datetime
import gzip
import pickle

from python_opensubtitles.pythonopensubtitles.opensubtitles import OpenSubtitles
from python_opensubtitles.pythonopensubtitles.utils import File
from urllib import request

valid_extensions = [".avi", ".mkv", ".mpeg", ".mpg", ".mp4"]
subtitles_extension = ".srt"
exclude_list_filename = "data/exclude.lst"


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
        if valid_extension in file:
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
    subtitles_filename = filename[:-3] + "srt"
    gz_file = subtitles_filename + ".gz"
    handle = request.urlopen(subtitles_url).read()
    with open(gz_file, 'wb') as outfile:
        outfile.write(handle)
    with gzip.open(gz_file, 'rb') as gz_file_handler:
        with open(os.path.join(dirname, subtitles_filename), 'wb') as outfile:
            outfile.write(gz_file_handler.read())
    os.remove(gz_file)

if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    print("Usage: ./synchro_subtitles.py <validDirectory>")
else:
    path = sys.argv[1]
    valid_files_in_directory = list_valid_files_in_directory(path)
    exclude_list = get_exclude_list()
    open_sub = OpenSubtitles()
    token = open_sub.login('login', 'password')
    for video_to_get_sub in valid_files_in_directory:
        if video_to_get_sub in exclude_list:
            continue
        sub_file = File(video_to_get_sub)
        data = open_sub.search_subtitles([
            {'sublanguageid': 'eng', 'moviehash': sub_file.get_hash(), 'moviebytesize': sub_file.size}
        ])
        try:
            subtitles_file = data[0]["SubDownloadLink"]
            download_and_unzip_file(subtitles_file, video_to_get_sub)
            print(datetime.datetime.now().isoformat(), " --- subtitle found for ", video_to_get_sub)
        except:
            print(datetime.datetime.now().isoformat(), " --- /!\ no subtitles found for ", video_to_get_sub, file=sys.stderr)
            exclude_list.append(video_to_get_sub)

    save_exclude_list(exclude_list)

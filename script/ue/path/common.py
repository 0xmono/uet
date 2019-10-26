import os

def get_child_dirs(somePath):
    return [dir for dir in os.listdir(somePath) if os.path.isdir(os.path.join(somePath, dir))]

def get_files(somePath):
    return [fileName for fileName in os.listdir(somePath) if os.path.isfile(os.path.join(somePath, fileName))]

def get_parent_dir(somePath):
    return os.path.abspath(os.path.join(somePath, os.pardir))
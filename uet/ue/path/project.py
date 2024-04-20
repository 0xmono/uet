import os
import logging
from .common import *

SOURCE_DIR = "Source"
PLUGINS_DIR = "Plugins"
LOGS_DIR = "Saved/Logs"
UPROJECT_EXTENSION = ".uproject"
TARGET_FILE_ENDING = ".Target.cs"

def get_project_name_from_project_file_path(filePath):
    if filePath.endswith(UPROJECT_EXTENSION):
        return os.path.splitext(os.path.basename(filePath))[0]

def is_valid_uproject_file(filePath):
    #logging.debug("is_valid_uproject_file " + filePath + " " + str(get_project_name_from_project_file_path(filePath)))
    return get_project_name_from_project_file_path(filePath) is not None

def get_project_name_from_path(somePath):
    if os.path.isfile(somePath):
        return get_project_name_from_project_file_path(somePath)
    elif os.path.isdir(somePath):
        projectFileName = get_project_file_name_from_repo_path(somePath)
        if projectFileName:
            return os.path.splitext(projectFileName)[0]

def is_valid_root_path(somePath):
    uprojectFileName = get_project_file_name_from_repo_path(somePath)
    return (uprojectFileName != None)

def get_project_file_name_from_repo_path(projectPath):
    for fileName in get_files(projectPath):
        if is_valid_uproject_file(fileName):
            return fileName

def get_project_file_path(projectPath):
    fileName = get_project_file_name_from_repo_path(projectPath)
    if fileName:
        return os.path.join(projectPath, fileName)

def get_root_path_from_path(somePath):
    currentPath = os.path.abspath(somePath)
    while True:
        if is_valid_root_path(currentPath):
            return currentPath
        prevPath = currentPath
        currentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
        if prevPath == currentPath:
            break

def get_project_target_files(projectPath):
    sourcePath = os.path.abspath(os.path.join(projectPath, SOURCE_DIR))
    if os.path.isdir(sourcePath):
        return [fn for fn in get_files(sourcePath) if fn.endswith(TARGET_FILE_ENDING)]

def get_plugins_path(rootPath):
    return os.path.join(rootPath, PLUGINS_DIR)
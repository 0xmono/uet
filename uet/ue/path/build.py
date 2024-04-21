import os
import logging
import ue
import ue.platform as ue_pfm
from .common import *

LOGS_DIR = "Saved/Logs"

def is_build_exe_file(filePath, platform=None):
    logging.debug(f"is_build_exe_file {filePath}")
    if not filePath:
        return False

    if platform:
        platformInterfaces = [platform]
    else:
        platformInterfaces = [ue_pfm.get_current_platform_interface()]
        if not platformInterfaces:
            logging.error("No platform interfaces")
            return False

    isBuildExeFile = any(pi.is_build_exe_file(filePath) for pi in platformInterfaces)
    logging.debug(f"is_build_exe_file {isBuildExeFile}")
    return isBuildExeFile

def get_name_from_path(somePath, platform=None):
    engineBinariesDir = os.path.normpath(os.path.join(somePath, 'Engine/Binaries'))
    childDirs = get_child_dirs(somePath)
    if os.path.isdir(engineBinariesDir):
        for fileName in [fn for fn in get_files(somePath) if is_build_exe_file(fn, platform)]:
            fileNameNoExt = os.path.splitext(os.path.basename(fileName))[0]
            projectName = ue.project.split_build_name(fileNameNoExt)[0]
            if projectName in childDirs:
                if all((dir in get_child_dirs(os.path.join(somePath, projectName))) for dir in ['Binaries', 'Content']):
                    return fileNameNoExt

def is_valid_root_path(somePath, platform=None):
    return get_name_from_path(somePath, platform)

def get_root_path_from_path(somePath, platform=None):
    currentPath = os.path.abspath(somePath)
    while True:
        if is_valid_root_path(currentPath, platform):
            return currentPath
        prevPath = currentPath
        currentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
        if prevPath == currentPath:
            break

def get_project_content_path(rootPath, projectName):
    return os.path.join(rootPath, projectName)

def get_logs_path(rootPath, projectName):
    return os.path.join(get_project_content_path(rootPath, projectName), LOGS_DIR)

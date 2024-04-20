import os
import logging
import ue
from .common import *

ENGINE_DIR = "Engine"
SOURCE_DIR = os.path.join(ENGINE_DIR, "Source")
SOURCE_RUNTIME_DIR = os.path.join(ENGINE_DIR, "Source")
PLUGINS_DIR = os.path.join(ENGINE_DIR, "Plugins")
SAVED_DIR = os.path.join(ENGINE_DIR, "Saved")
LOGS_DIR = os.path.join(ENGINE_DIR, "Logs")
VERSION_FILE_PATH = "Engine/Source/Runtime/Launch/Resources/Version.h"

def get_root_path_from_identifier(identifier):
    platformInterface = ue.platform.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    engineInstallations = platformInterface.get_all_engine_installations()
    return engineInstallations.get(identifier)

def get_identifier_from_root_path(rootPath):
    platformInterface = ue.platform.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    engineInstallations = platformInterface.get_all_engine_installations()
    for identifier, installationPath in engineInstallations.items():
        if rootPath == installationPath:
            return identifier

def is_valid_root_path(somePath):
    binariesDir = os.path.normpath(os.path.join(somePath, 'Engine/Binaries'))
    hasBinariesDir = os.path.isdir(binariesDir)
    if not hasBinariesDir:
        logging.debug(somePath + " is not a valid engine root directory because " + binariesDir + " is absent")
    
    buildDir = os.path.normpath(os.path.join(somePath, "Engine/Build"))
    hasBuildDir = os.path.isdir(buildDir)
    if not buildDir:
        logging.debug(somePath + " is not a valid engine root directory because " + buildDir + " is absent")

    return hasBinariesDir and hasBuildDir

def get_version_from_root_dir(rootPath):
    fullVersionFilePath = os.path.join(rootPath, VERSION_FILE_PATH)
    versionMajor = None
    versionMinor = None
    versionPatch = None
    if os.path.isfile(fullVersionFilePath):
        with open(fullVersionFilePath) as f:
            datafile = f.readlines()
            for line in datafile:
                # Just hack instead of c++ preprocessor
                if versionMajor is None and '#define' in line and 'ENGINE_MAJOR_VERSION' in line:
                    versionMajor = [s for s in line.split() if s.isdigit()][-1]
                if versionMinor is None and '#define' in line and 'ENGINE_MINOR_VERSION' in line:
                    versionMinor = [s for s in line.split() if s.isdigit()][-1]
                if versionPatch is None and '#define' in line and 'ENGINE_PATCH_VERSION' in line:
                    versionPatch = [s for s in line.split() if s.isdigit()][-1]
    return versionMajor, versionMinor, versionPatch

def get_engine_path(rootPath):
    #return "e:/projects/Unreal/4_20/Engine"
    #return "e:/prog/Epic/UE_4.20/Engine"
    return os.path.join(rootPath, ENGINE_DIR)

def get_plugins_path(rootPath):
    #return "e:/projects/Unreal/4_20/Engine/Plugins"
    #return "e:/prog/Epic/UE_4.20/Engine/Plugins"
    return os.path.join(rootPath, PLUGINS_DIR)

def get_relative_build_file_path():
    platformInterface = ue.platform.get_current_platform_interface()
    if not platformInterface:
        logging.error("Platform interface is None")
        return None

    return platformInterface.get_relative_build_file_path()

def get_logs_path(rootPath):
    return os.path.join(rootPath, LOGS_PATH)
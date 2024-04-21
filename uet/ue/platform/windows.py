import os
import sys
import logging
import platform
import win32api, win32con
import ue
from .base import UePlatformBase

INSTALLATION_SUB_KEY = "SOFTWARE\\Epic Games\\Unreal Engine\\Builds"
EXE_EXTENSION = ".exe"
EPIC_SETTINGS_PATH = "C:/ProgramData/Epic"
RELATIVE_BUILD_FILE_PATH = "Engine/Build/BatchFiles/Build.bat"

class UePlatformWindows(UePlatformBase):
    def get_launcher_installations_file_path(self):
        return os.path.join(os.path.normpath(EPIC_SETTINGS_PATH), "UnrealEngineLauncher", "LauncherInstalled.dat")

    def get_source_engine_installations(self):
        engineInstallations = {}
        userKeyPath = win32con.HKEY_CURRENT_USER
        regKeyHandle = None

        try:
            regKeyHandle = win32api.RegOpenKeyEx(userKeyPath, INSTALLATION_SUB_KEY, 0, win32con.KEY_READ)
            uniqueDirectories = [item[1] for item in engineInstallations]

            i = 0
            while True:
                try:
                    name, value, type = win32api.RegEnumValue(regKeyHandle, i)
                    logging.debug(str(name))
                    if name and value:
                        installLocation = os.path.normpath(value)
                        if ue.path.engine.is_valid_root_path(installLocation):
                            if installLocation in uniqueDirectories:
                                logging.warning(installLocation + " is duplicated, name " + (name))
                            else:
                                uniqueDirectories.append(installLocation)
                                engineInstallations[name] = installLocation
                        else:
                            logging.warning(installLocation + " is not a valid engine root directory")
                except Exception as e:
                    logging.debug(str(e))
                    break
                i = i + 1

        except Exception as e:
            logging.warning("Can't open registry key: " + str(userKeyPath) + "/" + str(INSTALLATION_SUB_KEY) + " because of " + str(e))
        finally:
            if regKeyHandle is not None:
                win32api.RegCloseKey(regKeyHandle)
                #regKeyHandle.Close()

        logging.debug("Source engine installations: " + str(engineInstallations))
        return engineInstallations

    def is_build_exe_file(self, filePath):
        return filePath.endswith(EXE_EXTENSION)

    def get_relative_build_file_path(self):
        return RELATIVE_BUILD_FILE_PATH

import os
import logging
import configparser
from .base import UePlatformBase
from ue import path as ue_path
import common as cm

SH_EXTENSION = ".sh"
UE_LAUNCHER_DIR_NAME = "UnrealEngineLauncher"
UE_LAUNCHER_CONFIG_NAME = "LauncherInstalled.dat"
UE_DIR_NAME = "UnrealEngine"
UE_CONFIG_NAME = "Install.ini"
INSTALLATIONS_SECTION = "Installations"
RELATIVE_BUILD_FILE_PATH = "Engine/Build/BatchFiles"

class UePlatformUnix(UePlatformBase):
    def get_epic_settings_path(self):
        userHomeDir = os.path.expanduser("~")
        return os.path.join(userHomeDir, self.get_relative_epic_settings_path())

    def get_relative_epic_settings_path(self) -> str:
        logging.error(f"{cm.get_func_name()} is NOT IMPLEMENTED for platform `{self.get_name()}`")
        return ""

    def get_launcher_installations_file_path(self):
        return os.path.join(self.get_epic_settings_path(), UE_LAUNCHER_DIR_NAME, UE_LAUNCHER_CONFIG_NAME)

    def get_source_engine_installations(self):
        engineInstallations = {}
        uniqueDirectories = []

        epicConfigDir = self.get_epic_settings_path()
        ueConfigPath = os.path.join(epicConfigDir, UE_DIR_NAME, UE_CONFIG_NAME)
        logging.debug("Config: " + str(ueConfigPath))

        config = configparser.ConfigParser()
        config.read(ueConfigPath)

        try:
            installationsSection = config[INSTALLATIONS_SECTION]
            for name in installationsSection:
                installLocation = os.path.normpath(installationsSection[name])
                if ue_path.engine.is_valid_root_path(installLocation):
                    if installLocation in uniqueDirectories:
                        logging.warning(installLocation + " is duplicated, name " + (name))
                    else:
                        uniqueDirectories.append(installLocation)
                        engineInstallations[name.upper().lstrip("{").rstrip("}")] = installLocation
                else:
                    logging.warning(installLocation + " is not a valid engine root directory")
        except Exception as e:
            logging.warning("Exception while trying to parse config file '" + ueConfigPath + "': " + str(e))

        logging.debug("SourceEngineInstallations: " + str(engineInstallations))

        return engineInstallations

    def is_build_exe_file(self, filePath):
        return filePath.endswith(SH_EXTENSION)

    def get_relative_build_file_path(self):
        return os.path.join(RELATIVE_BUILD_FILE_PATH, self.get_name(), "Build") + SH_EXTENSION

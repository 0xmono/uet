import os
import logging
import json
import ue

class UePlatformBase:
    def get_application_settings_path(self):
        logging.error("get_application_settings_path NOT IMPLEMENTED")
        return ""
    
    def get_launcher_settings_path(self):
        logging.error("get_launcher_settings_path NOT IMPLEMENTED")
        return ""

    def get_launcher_installations_file_path(self):
        logging.error("get_launcher_installations_file_path NOT IMPLEMENTED")
        return ""

    def get_source_engine_installations(self):
        logging.error("get_source_engine_installations NOT IMPLEMENTED")
        return {}

    def get_all_engine_installations(self):
        launcherEngineInstallations = self.get_launcher_engine_installations()
        sourceEngineInstallations = self.get_source_engine_installations()
        engineInstallations = {**launcherEngineInstallations, **sourceEngineInstallations}
        logging.debug("All engine installations: " + str(engineInstallations))
        return engineInstallations

    def read_launcher_installations(self):
        installations = {}
        filePath = os.path.normpath(self.get_launcher_installations_file_path())
        logging.debug("File path: " + filePath)

        with open(filePath) as fileContent:
            data = json.load(fileContent)
            if 'InstallationList' in data:
                for installation in data['InstallationList']:
                    if installation['AppName'] and installation['InstallLocation']:
                        installations[installation['AppName']] = os.path.normpath(installation['InstallLocation'])
            else:
                logging.info("No launcher installations found at " + filePath)
        
        logging.debug("Launcher installations found: " + str(installations))
        return installations

    def get_launcher_engine_installations(self):
        engineInstallations = {}
        launcherInstallationList = self.read_launcher_installations()
        
        for appName, installLocation in launcherInstallationList.items():
            if appName.startswith('UE_'):
                if ue.path.engine.is_valid_root_path(installLocation):
                    engineInstallations[appName[3:]] = installLocation
                else:
                    logging.warning(installLocation + " is not a valid engine root directory")

        logging.debug("Launcher engine installations found: " + str(engineInstallations))
        return engineInstallations

    def is_build_exe_file(self, filePath):
        logging.error("is_build_exe_file NOT IMPLEMENTED")
        return False

    def get_relative_build_file_path(self):
        raise NotImplementedError("Linux build is not implemented!")
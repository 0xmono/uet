import os
import logging
import ue
from .base import UeContextBase

class UeContextEngine(UeContextBase):
    def is_root_dir(somePath):
        return ue.path.engine.is_valid_root_path(somePath)

    def get_root_path(somePath):
        return UeContextEngine._get_root_path(somePath, UeContextEngine.is_root_dir)

    def construct(somePath):
        rootPath = UeContextEngine.get_root_path(somePath)
        if rootPath is not None:
            return UeContextEngine(rootPath)

    def __init__(self, inRootPath):
        UeContextBase.__init__(self, inRootPath)
        self.versionMajor, versionMinor, versionPatch = ue.path.get_version_from_root_dir(self.rootPath)
        self.projectName = ue.path.get_project_name_from_path(inRootPath)
        self.projectFilePath = ue.path.get_project_file_path(inRootPath)

    def getName(self):
        return "engine"

    def inspect(self, settings):
        versionMajor, versionMinor, versionPatch = ue.path.get_version_from_root_dir(self.rootPath)
        engineVersion = str(versionMajor) + '.' + str(versionMinor) + '.' + str(versionPatch)
        logging.info("Engine version: " + str(engineVersion))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()

    def get_all_plugins(self):
        pluginsDirectory = ue.path.engine.get_plugins_path(self.rootPath)
        return ue.path.plugins.read_plugins_from_directory(pluginsDirectory, False, 'Engine')

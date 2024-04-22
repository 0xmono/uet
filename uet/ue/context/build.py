import os
import logging
import ue
from .base import UeContextBase

class UeContextBuild(UeContextBase):
    def is_root_dir(somePath):
        return ue.path.build.is_valid_root_path(somePath)

    def get_root_path(somePath):
        return UeContextBuild._get_root_path(somePath, UeContextBuild.is_root_dir)

    def construct(somePath):
        rootPath = UeContextBuild.get_root_path(somePath)
        if rootPath is not None:
            return UeContextBuild(rootPath)

    def getName(self):
        return "build"

    def status(self, settings):
        buildName = ue.path.build.get_name_from_path(buildRootPath)
        projectName, target = ue.project.split_build_name(buildName)
        logging.info("ProjectName: " + str(projectName))
        logging.info("Target: " + str(target))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()

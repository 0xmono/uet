import re
import os
import sys
from time import gmtime, strftime
import subprocess as sp
from argparse import ArgumentParser
import logging
import common as cm
import ue
from ue import platform as ue_pfm
from build_config import BuildConfig

DEFAULT_TARGET = "Editor"
DEFAULT_CONFIG = "Development"
DEFAULT_PLATFORM = "Win64"

DISABLE_UNITY_BUILD_ARG = "-DisableUnity"
NO_PCH_ARG = "-NoPCH"
NO_SHARED_PCH_ARG = "-NoSharedPCH"

class BuildError(Exception):
    """Custom exception for build-related errors"""
    pass

def get_real_arg_values_list(argValue, allValue, dbgDescription):
    """Convert argument value to list with validation"""
    valuesList = None
    
    if isinstance(argValue, (list, str)):
        values = [argValue] if isinstance(argValue, str) else argValue
        if len(values) == 1 and values[0].lower() == "all":
            valuesList = allValue
        else:
            valuesList = values
    
    if valuesList is None:
        error_msg = f"Wrong type {dbgDescription} arg type: {type(argValue)} {argValue}"
        logging.error(error_msg)
        raise BuildError(error_msg)
        
    return valuesList


class ProjectBuilder:
    def __init__(self):
        self.config = None

    def run(self):
        self.config = self.process_args()
        if not self.config:
            return
            
        initResult = self.init(self.config.source_path)
        if initResult:
            buildFilePath, projectFilePath = initResult
            self.run_build(buildFilePath, projectFilePath)

    def process_args(self):
        parser = ArgumentParser()
        cm.init_arg_parser(parser)
        parser.add_argument("shellsource",
                            help="directory inside of UE project or build, set by calling shell", metavar="SHELL_SOURCE")
        parser.add_argument("-s", "--source", dest="source",
                            help="directory inside of UE project or build, set by user, overrides value of 'shellsource' argument",
                            metavar="SOURCE")
        parser.add_argument("-t", "--target", dest="target", nargs='+', default=DEFAULT_TARGET,
                            help="targets[s] to build. Use `status` script to find available targets. Use 'all' to build all available targets.",
                            metavar="TARGET")
        parser.add_argument("-c", "--config", dest="config", nargs='+', default=DEFAULT_CONFIG,
                            help=f"configuration type from {ue.project.ALL_CONFIGURATIONS}", metavar="CONFIG")
        parser.add_argument("-p", "--platform", dest="platform", nargs='+', default=DEFAULT_PLATFORM,
                            help=f"platform type from {ue.project.ALL_PLATFORMS}", metavar="PLATFORM")
        parser.add_argument("-e", "--definitions", dest="definitions", nargs='+',
                            help="Definition for compiler.",
                            metavar="DEFINITIONS")
        parser.add_argument("-u", "--nonunity",
                            action="store_true", dest="nonUnity", default=False,
                            help="non-unity build")
        parser.add_argument("-i", "--noprecompiledheaders",
                            action="store_true", dest="noPrecompiledHeaders", default=False,
                            help="not use precompiled headers")

        parsedArgs = parser.parse_args()
        self.onlyDebug = cm.process_parsed_args(parsedArgs)
        
        return BuildConfig.from_args(parsedArgs)

    def init(self, sourcePath):
        logging.debug(f"Input SourcePath: {sourcePath}")
        sourcePath = ue.path.project.get_root_path_from_path(sourcePath)
        logging.debug(f"Actual SourcePath: {sourcePath}")

        if os.path.isdir(sourcePath):
            projectFilePath = ue.path.get_project_file_path(sourcePath)
            logging.debug(f"ProjectFilePath: {projectFilePath}")
            if projectFilePath and os.path.isfile(projectFilePath):
                enginePath = ue.project.get_engine_root_path(projectFilePath)
                logging.debug(f"EnginePath: {enginePath}")
                if enginePath and os.path.isdir(enginePath):
                    buildFilePath = os.path.normpath(os.path.join(enginePath, ue.path.get_relative_build_file_path()))
                    logging.debug(f"BuildFilePath: {buildFilePath}")
                    if buildFilePath and os.path.isfile(buildFilePath):
                        return buildFilePath, projectFilePath
                    else:
                        logging.warning(f"BuildFilePath is invalid: {buildFilePath}")
                else:
                    logging.warning(f"EnginePath is invalid: {enginePath}")
            else:
                logging.warning(f"ProjectFilePath is invalid: {projectFilePath}")
        else:
            logging.warning(f"SourcePath is invalid: {sourcePath}")

    def run_build(self, buildFilePath, projectFilePath):
        logging.debug(f"Run build: [{buildFilePath}, {projectFilePath}, {self.config}]")
        projectName = ue.path.get_project_name_from_project_file_path(projectFilePath)
        projectPath = os.path.dirname(projectFilePath)

        targets = get_real_arg_values_list(self.config.target, ue.project.get_build_targets(projectPath), "target")
        if not targets:
            return

        configurations = get_real_arg_values_list(self.config.config, ue.project.ALL_CONFIGURATIONS, "configuration")
        if not configurations:
            return

        platforms = get_real_arg_values_list(self.config.platform, ue.project.ALL_PLATFORMS, "platform")
        if not platforms:
            return

        logging.info(f"\nBuild platforms: {platforms}")
        logging.info(f"Build configurations: {configurations}")
        logging.info(f"Build targets: {targets}\n")

        for platform in platforms:
            logging.info(f"\n{'#'*35} Building {platform} platform {'#'*35}\n")
            for config in configurations:
                for target in targets:
                    self.run_single_build(buildFilePath, projectFilePath, projectName, config, target, platform)

    def run_single_build(self, buildFilePath, projectFilePath, projectName, config, target, platform):
        logging.info(f"\n{'='*35} Building {platform}_{config}_{target.capitalize()} {'='*35}\n")
        buildTarget = self.get_target_arg(projectName, target)

        command = [buildFilePath, buildTarget, platform, config, projectFilePath]

        if self.config.definitions:
            command.append(f"-define:{' '.join(self.config.definitions)}")

        if self.config.non_unity:
            command.append(DISABLE_UNITY_BUILD_ARG)

        if self.config.no_precompiled_headers:
            command.append(NO_SHARED_PCH_ARG)
            command.append(NO_PCH_ARG)

        logging.info(f"Running command: {command}")
        
        if not self.config.debug_only:
            try:
                process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise BuildError(f"Build failed with code {process.returncode}\n{stderr.decode()}")
                    
                if stdout:
                    logging.info(stdout.decode())
                if stderr:
                    logging.error(stderr.decode())
                    
            except Exception as e:
                raise BuildError(f"Build process failed: {e}")

    def get_target_arg(self, projectName, target):
        targetArg = ue.project.create_build_name(projectName, target)
        logging.debug("Target arg: " + str(targetArg))
        return targetArg

def main():
    print("Build Unreal Engine project")
    builder = ProjectBuilder()
    builder.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

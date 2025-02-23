import os
import sys
import logging
import platform
import json
import copy
import ue
from typing import Optional, List, Dict, Tuple, Any

ALL_TARGETS = ["Editor", "Game", "Client", "Server"]
TARGET_BIULD_SUFFUX = {
    "Editor": "Editor",
    "Game": "",
    "Client": "Client",
    "Server": "Server"
}

ALL_CONFIGURATIONS = ["Debug", "Development", "Test", "Shipping"]
ALL_PLATFORMS = ["Win64", "Linux", "Mac"]

# Return [project name, target name] if possible, else None
def split_build_name(buildName: str) -> Optional[Tuple[str, str]]:
    """Split build name into project name and target name."""
    for target, suffix in TARGET_BIULD_SUFFUX.items():
        if buildName.lower().endswith(suffix.lower()):
            projectName = buildName[:-len(suffix)] if suffix else buildName
            return (projectName, target)
    return None

def get_target_from_build_name(buildName, projectName):
    suffix = buildName[len(projectName):]
    try:
        reverceDict = {v: k for k, v in TARGET_BIULD_SUFFUX.items()}
        return reverceDict[suffix]
    except KeyError:
        logging.warning("Unknown suffix: " + str(suffix))
        return suffix

# Get build name for project name and target name
def create_build_name(projectName, targetName):
    if targetName.lower() == "game":
        return projectName
    else:
        return projectName + targetName.capitalize()

def has_build_target(projectPath, buildTargetName):
    buildTargets = get_build_targets(projectPath)
    return (buildTargetName in buildTargets)

def get_build_targets(projectPath):
    projectName = ue.path.project.get_project_name_from_path(projectPath)
    if projectName:
        targetFiles = ue.path.project.get_project_target_files(projectPath)
        logging.debug("Target files: " + str(targetFiles))
        return [get_target_from_build_name(tf[:-len(ue.path.TARGET_FILE_ENDING)], projectName) for tf in targetFiles]

def get_plugins(projectFilePath: str) -> Dict[str, Dict[str, Any]]:
    """Get plugins configuration from project file."""
    plugins: Dict[str, Dict[str, Any]] = {}
    
    if not (projectFilePath and os.path.isfile(projectFilePath)):
        return plugins
        
    try:
        with open(projectFilePath) as projectCfg:
            data = json.load(projectCfg)
            for plugin_data in data.get('Plugins', []):
                plugin_name = plugin_data.get('Name')
                if plugin_name:
                    pluginStatus = str(plugin_data.get('Enabled', '')).lower()
                    enabled = pluginStatus == 'true'
                    if pluginStatus != 'true' and pluginStatus != 'false':
                        logging.warning(f"Invalid plugin status for {plugin_name}: {pluginStatus}")
                    plugins[plugin_name] = {'Enabled': enabled}
                    logging.debug(f"Plugin {plugin_name} enable status in project file: {enabled}")
                
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Failed to read project file {projectFilePath}: {e}")
        
    return plugins


def update_plugins_by_project_file(projectFilePath, plugins):
    projectFilePlugins = get_plugins(projectFilePath)

    for pluginName in projectFilePlugins:
        pluginInfo = plugins.get(pluginName)
        pluginDescr = projectFilePlugins[pluginName]
        if pluginInfo:
            pluginInfo['InProjectFile'] = True

            if not pluginInfo['Enabled'] and pluginDescr['Enabled']:
                pluginInfo['Enabled'] = True
                logging.debug("Setting enabled plugin " + pluginName)
            if pluginInfo['Enabled'] and not pluginDescr['Enabled']:
                pluginInfo['Enabled'] = False
                logging.debug("Setting disabled plugin " + pluginName)
        else:
            logging.warning("Invalid plugin " + pluginName + " in " + projectFilePath)

    return plugins

def get_engine_id(projectFilePath):
    #EngineAssociation": "4.20"
    with open(projectFilePath) as projectCfg:
        data = json.load(projectCfg)
        if 'EngineAssociation' in data:
            return data['EngineAssociation'].upper().lstrip("{").rstrip("}")

def get_engine_root_path(projectFilePath):
    #return "e:/projects/Unreal/4_20"
    #return "e:/prog/Epic/UE_4.20"
    engineId = get_engine_id(projectFilePath)
    if engineId:
        return ue.path.engine.get_root_path_from_identifier(engineId)

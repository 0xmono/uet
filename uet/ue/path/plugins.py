import os
import logging
from .common import *

PLUGINS_PATH = "Plugins"
PLUGIN_FILE_EXTENSION = ".uplugin"

def read_plugins_from_directory(parentDirPath, ebabledByDefault = False, source = None):
    plugins = {}
    if os.path.isdir(parentDirPath):
        for pluginDir in get_child_dirs(parentDirPath):
            pluginPath = os.path.join(parentDirPath, pluginDir)
            pluginFiles = [fn for fn in get_files(pluginPath) if fn.endswith(PLUGIN_FILE_EXTENSION)]
            #logging.debug("In directory '" + str(pluginPath) + "', plugin files " + str(pluginFiles))
            if len(pluginFiles) > 1:
                logging.warning("More then one plugin file in directory '" + str(pluginPath) + "', choosing '" + str(pluginFiles[0]) + "'")
            if pluginFiles:
                pluginName = os.path.splitext(os.path.basename(pluginFiles[0]))[0]
                plugins[pluginName] = { 'Path' : pluginFiles[0], 'Enabled' : ebabledByDefault }
                if source:
                    plugins[pluginName]['Source'] = source
                if not is_valid_plugin_directory(pluginPath):
                    logging.warning("Plugin directory seems broken: " + str(pluginPath))
            else:
                plugins = {**plugins, **read_plugins_from_directory(pluginPath, ebabledByDefault, source)}
    return plugins

def is_valid_plugin_directory(pluginPath):
    pluginFiles = [fn for fn in get_files(pluginPath) if fn.endswith(PLUGIN_FILE_EXTENSION)]
    hasPluginFile = (len(pluginFiles) > 0)

    contentDir = os.path.normpath(os.path.join(pluginPath, 'Content'))
    hasContentDir = os.path.isdir(contentDir)

    sourceDir = os.path.normpath(os.path.join(pluginPath, 'Source'))
    hasSourceDir = os.path.isdir(sourceDir)

    isValidPluginDir = hasPluginFile and (hasContentDir or hasSourceDir)

    if not isValidPluginDir:
        logging.debug(pluginPath + " is not a valid plugin directory " + contentDir + " " + sourceDir)
    
    return isValidPluginDir

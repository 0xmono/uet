import os
import logging
import ue
from .base import UeContextBase
from .engine import UeContextEngine

class UeContextProject(UeContextBase):
    def is_root_dir(somePath):
        return ue.path.project.is_valid_root_path(somePath)

    def get_root_path(somePath):
        return UeContextProject._get_root_path(somePath, UeContextProject.is_root_dir)

    def construct(somePath):
        rootPath = UeContextProject.get_root_path(somePath)
        if rootPath is not None:
            return UeContextProject(rootPath)

    def __init__(self, inRootPath):
        UeContextBase.__init__(self, inRootPath)
        self.projectName = ue.path.project.get_project_name_from_path(inRootPath)
        self.projectFilePath = ue.path.project.get_project_file_path(inRootPath)
        
        if self.projectFilePath and os.path.isfile(self.projectFilePath):
            self.engineId = ue.project.get_engine_id(self.projectFilePath)
            logging.debug("Engine Id: " + str(self.engineId))
            
            self.enginePath = ue.project.get_engine_root_path(self.projectFilePath)
            logging.debug("Engine Path: " + str(self.enginePath))
            self.contextEngine = None

            if self.enginePath:
                self.contextEngine = UeContextEngine.construct(self.enginePath)

    def getName(self):
        return "project"

    def inspect(self, settings):
        logging.info("Project Name: " + str(self.projectName))
        
        logging.debug("ProjectFilePath: " + str(self.projectFilePath))

        if self.projectFilePath and os.path.isfile(self.projectFilePath):
            logging.info("Engine Id: " + str(self.engineId))
            logging.info("Engine Path: " + str(self.enginePath))

            if self.contextEngine:
                self.contextEngine.inspect(settings)

            buildTargets = ue.project.get_build_targets(self.rootPath)
            logging.info("Build targets: " + str(buildTargets))

            if settings.plugins or settings.projectPlugins or settings.allPlugins:

                plugins = self.get_plugins()

                enabledPluginNames = [pluginName for pluginName in plugins if plugins[pluginName]['Enabled'] == True]
                if enabledPluginNames:
                    logging.info("Enabled plugins:")
                    for pluginName in enabledPluginNames:
                        pluginInfo = plugins[pluginName]
                        dbgStr = "\t" + pluginName
                        if pluginInfo['Source'] == 'Engine':
                            dbgStr += " (Engine)"
                        logging.info(dbgStr)

                disabledPluginNames = [pluginName for pluginName in plugins if plugins[pluginName]['Enabled'] == False]
                if disabledPluginNames and (settings.projectPlugins or settings.allPlugins):
                    logging.info("Available plugins:")
                    for pluginName in disabledPluginNames:
                        pluginInfo = plugins[pluginName]
                        if settings.allPlugins or pluginInfo.get('InProjectFile'):
                            dbgStr = "\t" + pluginName
                            if pluginInfo['Source'] == 'Engine':
                                dbgStr += " (Engine)"
                            logging.info(dbgStr)
        else:
            logging.warning("ProjectFilePath is invalid: " + str(self.projectFilePath))

    def build(self, settings):
        raise NotImplementedError()

    def view_logs(self, settings):
        raise NotImplementedError()

    def has_plugin(self, pluginName):
        plugins = self.get_plugins()
        return (pluginName in plugins)

    def is_plugin_enabled(self, pluginName):
        plugins = self.get_plugins()
        return (pluginName in plugins and plugins[pluginName].get('Enabled'))

    def get_plugins(self):
        plugins = self.get_all_plugins()
        return ue.project.update_plugins_by_project_file(self.projectFilePath, plugins)

    def get_all_plugins(self):
        pluginsDirectory = ue.path.project.get_plugins_path(self.rootPath)
        projectPlugins = ue.path.plugins.read_plugins_from_directory(pluginsDirectory, True, 'Project')
        enginePlugins = self.contextEngine.get_all_plugins() if self.contextEngine else {}

        commonPlugins = projectPlugins.keys() & enginePlugins.keys()
        if commonPlugins:
            logging.warning("Duplicated plugins in project and in engine: " + str(commonPlugins))

        plugins = {**projectPlugins, **enginePlugins}
        return plugins
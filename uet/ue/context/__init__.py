import logging
from .project import UeContextProject
from .build import UeContextBuild
from .engine import UeContextEngine

def get_context_interface(somePath):
    context = UeContextProject.construct(somePath)
    if context is None:
        context = UeContextBuild.construct(somePath)
        if context is None:
            context = UeContextEngine.construct(somePath)
    
    if context:
        logging.debug("Found Unreal Engine " + context.getName() + " root directory, using it '" + context.rootPath + "'");

    return context

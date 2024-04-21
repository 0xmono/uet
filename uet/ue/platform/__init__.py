import os
import sys
import logging
import platform

def get_platform_interface(platformName):
    if platformName  == 'Linux':
        from .linux import UePlatformLinux
        return UePlatformLinux()
    elif platformName == 'Windows':
        from .windows import UePlatformWindows
        return UePlatformWindows()
    elif platformName == 'Darwin':
        from .mac import UePlatformMac
        return UePlatformMac()

def get_current_platform_interface():
    return get_platform_interface(platform.system())

def get_all_platform_interfaces():
    return {
        'Linux': get_platform_interface('Linux'),
        'Windows': get_platform_interface('Windows'),
        'Darwin': get_platform_interface('Darwin'),
    }

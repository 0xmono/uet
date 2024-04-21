from .unix import UePlatformUnix

EPIC_CONFIG_PATH = ".config/Epic"

class UePlatformLinux(UePlatformUnix):
    def get_name(self):
        return "Linux"

    def get_relative_epic_settings_path(self):
        return EPIC_CONFIG_PATH

    def get_default_build_platform(self):
        return "Linux"

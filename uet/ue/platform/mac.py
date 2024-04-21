from .unix import UePlatformUnix

EPIC_CONFIG_PATH = "Library/Application Support/Epic"

class UePlatformMac(UePlatformUnix):
    def get_name(self):
        return "Mac"

    def get_relative_epic_settings_path(self):
        return EPIC_CONFIG_PATH

    def get_default_build_platform(self):
        return "Mac"

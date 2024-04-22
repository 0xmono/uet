from .unix import UePlatformUnix

# Launcher config: no launcher on Linux for now
# Source config: `~/Library/Application Support/Epic/UnrealEngine/Install.ini`

EPIC_CONFIG_PATH = ".config/Epic"

class UePlatformLinux(UePlatformUnix):
    def get_name(self):
        return "Linux"

    def get_relative_epic_settings_path(self):
        return EPIC_CONFIG_PATH

    def get_default_build_platform(self):
        return "Linux"

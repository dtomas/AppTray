from apptray.category import Category

CATEGORY_NETWORK = Category(10, "Network", _("Network"), ['applications-internet'])
CATEGORY_OFFICE = Category(20, "Office", _("Office"), ['applications-office'])
CATEGORY_AUDIOVIDEO = Category(30, "AudioVideo", _("Multimedia"), ['applications-multimedia'])
#CATEGORY_AUDIO = Category("Audio", _("Audio"), _("Audio"))
#CATEGORY_VIDEO = Category("Video", _("Video"), _("Video"))
CATEGORY_GRAPHICS = Category(40, "Graphics", _("Graphics"), ['applications-graphics'])
CATEGORY_DEVELOPMENT = Category(60, "Development", _("Development"), ['applications-development'])
CATEGORY_SCIENCE = Category(80, "Science", _("Science"), ['applications-science'])
CATEGORY_GAME = Category(70, "Game", _("Games"), ['applications-games'])
CATEGORY_UTILITY = Category(50, "Utility", _("Utilities"), ['applications-accessories'])
CATEGORY_UNKNOWN = Category(90, "Unknown", _("Other"), ['applications-other'])
CATEGORY_SETTINGS_DESKTOP = Category(110, "Settings", _("Desktop Settings"), ['preferences-desktop'])
CATEGORY_SETTINGS_SYSTEM = Category(110, "SystemSettings", _("System Settings"), ['preferences-system'])
CATEGORY_SYSTEM = Category(100, "System", _("System"), ['applications-system'])
CATEGORY_APPLETS = Category(120, "ROX-Applets", _("Applets"), ['applications-other'])

# subcategories:
# Viewer -> Graphics
# DesktopSettings -> Settings
# HardwareSettings -> Settings
# Player -> AudioVideo
# Recorder -> AudioVideo
# DiscBurning -> AudioVideo

categories = [CATEGORY_NETWORK, 
              CATEGORY_OFFICE, 
              CATEGORY_AUDIOVIDEO, 
              CATEGORY_GRAPHICS, 
              CATEGORY_UTILITY,
              CATEGORY_DEVELOPMENT,
              CATEGORY_SCIENCE,
              CATEGORY_GAME,
              CATEGORY_SYSTEM,
              CATEGORY_UNKNOWN,
              CATEGORY_SETTINGS_SYSTEM,
              CATEGORY_SETTINGS_DESKTOP,
              CATEGORY_APPLETS]


def get(*category_ids):
    category_ids = set(category_ids)
    if "Office" in category_ids:
        return CATEGORY_OFFICE
    if "Graphics" in category_ids:
        return CATEGORY_GRAPHICS
    if "Development" in category_ids:
        return CATEGORY_DEVELOPMENT
    if "Science" in category_ids:
        return CATEGORY_SCIENCE
    if "Education" in category_ids:
        return CATEGORY_SCIENCE
    if "Game" in category_ids:
        return CATEGORY_GAME
    if set(["System", "Settings"]).intersection(category_ids):
        return CATEGORY_SETTINGS_SYSTEM
    if "HardwareSettings" in category_ids:
        return CATEGORY_SETTINGS_SYSTEM
    if "DesktopSettings" in category_ids:
        return CATEGORY_SETTINGS_DESKTOP
    if "Settings" in category_ids:
        return CATEGORY_SETTINGS_DESKTOP
    if "System" in category_ids:
        return CATEGORY_SYSTEM
    if "Utility" in category_ids:
        return CATEGORY_UTILITY
    if "Network" in category_ids:
        return CATEGORY_NETWORK
    if "AudioVideo" in category_ids:
        return CATEGORY_AUDIOVIDEO
    if "Video" in category_ids:
        return CATEGORY_AUDIOVIDEO
    if "Audio" in category_ids:
        return CATEGORY_AUDIOVIDEO
    if "ROX-Applets" in category_ids:
        return CATEGORY_APPLETS
    return CATEGORY_UNKNOWN

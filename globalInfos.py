# bot itself
TOKEN_PATH = "./token.txt"
BOT_ID = 1131514655404199936

# owner only features
OWNER_USERS = [579288989505421349]
GLOBAL_LOG_CHANNEL = 1132693034673389659
RESTRICT_TO_SERVERS = None # 'None' alone : enable everywhere, 'None' in the list : enable in DMs

# server settings
ALL_SERVER_SETTINGS_PATH = "./allServerSettings.json"
SERVER_SETTINGS_DEFAULTS = {
    "adminRoles" : [],
    "paused" : False,
    "restrictToChannel" : None,
    "restrictToRoles" : [],
    "restrictToRolesInverted" : False
}
CHANNEL_ID_LEN = 19
ROLE_ID_LEN = 19
MAX_ROLES_PER_LIST = 10

# texts
NO_PERMISSION_TEXT = "You don't have permission to do this"
UNKNOWN_ERROR_TEXT = "Unknown error happened"
MESSAGE_TOO_LONG_TEXT = "Message too long"
OWNER_ONLY_BADGE = "[Owner only]"
ADMIN_ONLY_BADGE = "[Admin only]"

# shape viewer
INITIAL_SHAPE_SIZE = 500
SHAPE_COLORS = ["u","r","g","b","c","p","y","w","k"]
SHAPE_LAYER_SEPARATOR = ":"
SHAPE_NOTHING_CHAR = "-"
SHAPE_CHAR_REPLACEMENT = {
    "m" : "p" # change magenta to purple
}

# display parameters
SHAPES_PER_ROW = 8
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 100
DEFAULT_SHAPE_SIZE = 56
VIEWER_3D_LINK_START = "https://shapez.soren.codes/shape?identifier="
VIEWER_3D_CHAR_REPLACEMENT = {
    ":" : "%3A"
}

# game infos
GI_RESEARCH_PATH = "./gameInfos/research.json"
GI_BUILDINGS_PATH = "./gameInfos/buildings.json"
GI_ISLANDS_PATH = "./gameInfos/islands.json"

# other
MESSAGE_MAX_LENGTH = 2000
DEFAULT_MAX_FILE_SIZE = 26_214_400 # 25 mebibytes
INVALID_SHAPE_CODE_REACTION = "\u2753"
BOT_MENTIONED_REACTION = "\U0001F916"
IMAGE_FILE_TOO_BIG_PATH = "./imageFileTooBig.png"
# bot itself
TOKEN_PATH = "./token.txt"
BOT_ID = 1131514655404199936

# owner only features
OWNER_USERS = [579288989505421349]
GLOBAL_LOG_CHANNEL = 1132693034673389659

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
NO_PERMISSION_TEXT = "You don't have the permission to do this"
UNKNOWN_ERROR_TEXT = "Unknown error happened"

# shape viewer
INITIAL_SHAPE_SIZE = 500
SHAPE_COLORS = ["u","r","g","b","c","p","y","w","k"]
SHAPE_LAYER_SEPARATOR = ":"
SHAPE_NOTHING_CHAR = "-"

# display parameters
SHAPES_PER_ROW = 8
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 100
DEFAULT_SHAPE_SIZE = 56
VIEWER_3D_LINK_START = "https://shapez.soren.codes/shape?identifier="
VIEWER_3D_CHAR_REPLACEMENT = {
    ":" : "%3A"
}

# other
MESSAGE_MAX_LENGTH = 2000
INVALID_SHAPE_CODE_REACTION = "\u2753"
LOADING_GIF_PATH = "./loading.gif"
SEND_LOADING_GIF_FOR_NUM_CHARS_SHAPE_VIEWER = 1000
SEND_LOADING_GIF_FOR_NUM_CHARS_OP_GRAPH = 50
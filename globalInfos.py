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
LEVEL_SHAPES = [ # different shapes between full and demo + too lazy to update every version
    "CuCuCuCu",
    "RuRu----",
    "Cu------",
    "Cu------",
    "CuRuCuCu",

    "--RuRuRu:----Cu--",
    "CuSuCuSu",
    "SuSuSu--:CuCuCuRu",
    "CuCuRuRu:CbCbSbSb",
    "CbCuCbCu:RuRbRuRb:SbSuSbSu",

    "SrRbRbRb:--SrCgSr:--CuCuCu",
    "CgRgCgCu:Sr--SrSr:CrRrCrCr:SbSuSbSb",
    "CuRuCuCu:CcCcCcCc",
    "RrCrRrCr:RwCwRwCw:CpCpCpCp:--Sy--Sy",
    "CwRwCwCw:P-P-P-P-:CcCcCcCc",

    "RwCbCgCr:CyCcRwCp",
    "cwCbCgCr:CyCccwCp",
    "CrRpcwcw:cwRbCccw:cwcwCgRy:CpcwcwRr",
    "CwRwcrcp:ccRwCwcb:cgcyCwRw:RwcrcpCw",
    "P-P-P-P-:SrSrP-P-:crcrcrcr:P-P-cwcw",
]

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
BOT_MENTIONED_REACTION = "\U0001F916"
BP_VERSION_REACTION_A = "\U0001f1e6"
BP_VERSION_REACTION_DOT = "\u23fa"
BP_VERSION_REACTION_UNITS = {str(i) : f"{i}\ufe0f\u20e3" for i in range(10)}
BP_VERSION_REACTION_TENS = {str(i) : v for i,v in enumerate([
    1159909533074866286,1159909535872471162,1159909537944457226,
    1159909542193270824,1159909546735702108,1159909549323587757,
    1159909551697576056,1159909554532913203,1159909556336468008,
    1159909559066964110
])}
BP_VERSION_REACTION_TENTHS = {str(i) : v for i,v in enumerate([
    1159909769876877352,1159909772133400707,1159909773643358228,
    1159909775526592512,1159909784305283133,1159909786956087326,
    1159909788130476124,1159909789741105282,1159909792106676405,
    1159909793578877028
])}
IMAGE_FILE_TOO_BIG_PATH = "./imageFileTooBig.png"
ALPHA_BP_VERSIONS = {
    1005 : "3",
    1008 : "4",
    1009 : "5",
    1013 : "6",
    1015 : "6.2",
    1018 : "7",
    1019 : "7.3",
    1022 : "7.4",
    1024 : "8",
    1027 : "10.2",
    1029 : "11",
    1030 : "12"
}
LATEST_GAME_VERSIONS = (1015,1030)
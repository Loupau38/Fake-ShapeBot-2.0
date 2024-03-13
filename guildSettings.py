import globalInfos
import json

_SETTINGS_DEFAULTS = {
    "adminRoles" : [],
    "paused" : False,
    "restrictToChannel" : None,
    "restrictToRoles" : [],
    "restrictToRolesInverted" : False,
    "usageCooldown" : 0,
    "antispamEnabled" : True,
    "antispamAlertChannel" : None
}
propertyTypes = list|bool|None|int
_guildSettings:dict[int,dict[str,propertyTypes]]

def _saveSettings() -> None:

    with open(globalInfos.GUILD_SETTINGS_PATH,"w",encoding="utf-8") as f:
        json.dump(_guildSettings,f)

def _createGuildDefaults(guildId:int) -> None:

    if _guildSettings.get(guildId) is None:
        _guildSettings[guildId] = {}

    curGuildSettings = _guildSettings[guildId]

    defaultObj = object()
    for key,value in _SETTINGS_DEFAULTS.items():
        if curGuildSettings.get(key,defaultObj) is defaultObj:
            if type(value) in (list,dict):
                toSetValue = value.copy()
            else:
                toSetValue = value
            curGuildSettings[key] = toSetValue

    _saveSettings()

def _load() -> None:

    global _guildSettings

    try:

        with open(globalInfos.GUILD_SETTINGS_PATH,encoding="utf-8") as f:
            _guildSettings = json.load(f)

    except FileNotFoundError:

        _guildSettings = {}
        _saveSettings()

    _guildSettings = {int(k) : v for k,v in _guildSettings.items()}

_load()

# doesn't need to be async but kept just in case
async def setGuildSetting(guildId:int,property:str,value:propertyTypes) -> None:

    _createGuildDefaults(guildId)
    _guildSettings[guildId][property] = value
    _saveSettings()

async def getGuildSettings(guildId:int) -> dict[str,propertyTypes]:

    _createGuildDefaults(guildId)
    return _guildSettings[guildId]
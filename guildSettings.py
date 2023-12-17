import globalInfos
import json

_SETTINGS_DEFAULTS = {
    "adminRoles" : [],
    "paused" : False,
    "restrictToChannel" : None,
    "restrictToRoles" : [],
    "restrictToRolesInverted" : False
}

def _saveSettings() -> None:

    with open(globalInfos.ALL_SERVER_SETTINGS_PATH,"w",encoding="utf-8") as f:
            json.dump(_guildSettings,f)

def _createGuildDefaults(guildId:int) -> None:

    if _guildSettings.get(guildId) is None:
        _guildSettings[guildId] = {k : (v.copy() if type(v) in (list,dict) else v) for k,v in _SETTINGS_DEFAULTS.items()}
    _saveSettings()

def _load() -> None:

    global _guildSettings

    try:

        with open(globalInfos.ALL_SERVER_SETTINGS_PATH,encoding="utf-8") as f:
            _guildSettings = json.load(f)

    except FileNotFoundError:

        _guildSettings = {}
        _saveSettings()

    _guildSettings = {int(k) : v for k,v in _guildSettings.items()}

_load()

# doesn't need to be async but kept just in case
async def setGuildSetting(guildId:int,property:str,value:list|bool|None|int) -> None:

    _createGuildDefaults(guildId)
    _guildSettings[guildId][property] = value
    _saveSettings()

async def getGuildSettings(guildId:int) -> dict[str,list|bool|None|int]:

    _createGuildDefaults(guildId)
    return _guildSettings[guildId]
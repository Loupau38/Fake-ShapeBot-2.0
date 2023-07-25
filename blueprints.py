import gzip
import base64
import json
PREFIX = "SHAPEZ2"
SEPARATOR = "-"
SUFFIX = "$"
def decodeBlueprint(rawBlueprint:str) -> tuple[dict,int]:
    if rawBlueprint.startswith(PREFIX):
        rawBlueprint = rawBlueprint[len(PREFIX):]
    else:
        raise ValueError("doesn't start with prefix")
    if rawBlueprint.startswith(SEPARATOR):
        rawBlueprint = rawBlueprint[len(SEPARATOR):]
    else:
        raise ValueError("no separator after prefix")
    rawBlueprint = rawBlueprint.split(SEPARATOR)
    if len(rawBlueprint) == 0:
        raise ValueError("nothing after first separator")
    if len(rawBlueprint) == 1:
        raise ValueError("no separator after version number")
    if len(rawBlueprint) > 2:
        raise ValueError("more separators than expected")
    try:
        majorVersion = int(rawBlueprint[0])
    except ValueError:
        raise ValueError("version number not a number")
    rawBlueprint = rawBlueprint[1]
    if rawBlueprint.endswith(SUFFIX):
        rawBlueprint = rawBlueprint[:-len(SUFFIX)]
    else:
        raise ValueError("doesn't end with suffix")
    return json.loads(gzip.decompress(base64.b64decode(rawBlueprint.encode()))), majorVersion
def encodeBlueprint(blueprint:dict,majorVersion:int) -> str:
    blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint).encode())).decode()
    blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    return blueprint
def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = decodeBlueprint(blueprint)
    blueprint["V"] = version
    return encodeBlueprint(blueprint,majorVersion)
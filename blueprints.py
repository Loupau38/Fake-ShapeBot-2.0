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

    try:
        rawBlueprint = rawBlueprint.encode()
    except Exception:
        raise ValueError("can't encode in bytes")
    try:
        rawBlueprint = base64.b64decode(rawBlueprint)
    except Exception:
        raise ValueError("can't decode from base64")
    try:
        rawBlueprint = gzip.decompress(rawBlueprint)
    except Exception:
        raise ValueError("can't gzip decompress")
    try:
        rawBlueprint = json.loads(rawBlueprint)
    except Exception:
        raise ValueError("can't parse json")

    return rawBlueprint, majorVersion

def encodeBlueprint(blueprint:dict,majorVersion:int) -> str:
    blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint).encode())).decode()
    blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    return blueprint

def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = decodeBlueprint(blueprint)
    blueprint["V"] = version
    try:
        blueprint = encodeBlueprint(blueprint,majorVersion)
    except Exception:
        raise ValueError("error while encoding blueprint")
    return blueprint

def getBlueprintInfo(blueprint:dict,*,version:bool=False,numBuildings:bool=False,size:bool=False) -> dict[str]:

    if type(blueprint) != dict:
        raise ValueError("Given 'blueprint' argument not a dict")

    toReturn = {}

    if version:

        versionNum = blueprint.get("V")

        if versionNum is None:
            raise ValueError("No version key")

        if type(versionNum) != int:
            raise ValueError("Version not an int")

        toReturn["version"] = versionNum

    if numBuildings or size:

        blueprintBP = blueprint.get("BP")

        if blueprintBP is None:
            raise ValueError("No blueprint key")

        if type(blueprintBP) != dict:
            raise ValueError("Blueprint not a dict")

        blueprintBPEntries = blueprintBP.get("Entries")

        if blueprintBPEntries is None:
            raise ValueError("No entries key")

        if type(blueprintBPEntries) != list:
            raise ValueError("Entries not a list")

    if numBuildings:
        toReturn["numBuildings"] = len(blueprintBPEntries)

    if size:

        def specialMin(num1:int|None,num2:int|None) -> int:
            if num1 is None:
                return num2
            if num2 is None:
                return num1
            return min(num1,num2)
        def specialMax(num1:int|None,num2:int|None) -> int:
            if num1 is None:
                return num2
            if num2 is None:
                return num1
            return max(num1,num2)

        minX = minY = minZ = maxX = maxY = maxZ = None

        for i,entry in enumerate(blueprintBPEntries):

            if type(entry) != dict:
                raise ValueError(f"Entry {i} not a dict")

            x = entry.get("X")
            y = entry.get("Y")
            z = entry.get("L")

            for value,text in zip((x,y,z),("x","y","z")):
                if type(value) != int:
                    raise ValueError(f"{text} of entry {i} not an int")

            minX, minY, minZ = [specialMin(v1,v2) for v1,v2 in zip((minX,minY,minZ),(x,y,z))]
            maxX, maxY, maxZ = [specialMax(v1,v2) for v1,v2 in zip((maxX,maxY,maxZ),(x,y,z))]

        if minX is None:
            toReturn["size"] = (0,0,0)
        else:
            toReturn["size"] = (maxX-minX+1,maxY-minY+1,maxZ-minZ+1)

    return toReturn
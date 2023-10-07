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
    try:
        blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint,separators=(",",":")).encode())).decode()
        blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    except Exception:
        raise ValueError("error while encoding blueprint")
    return blueprint

def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = decodeBlueprint(blueprint)
    blueprint["V"] = version
    blueprint = encodeBlueprint(blueprint,majorVersion)
    return blueprint

def getBlueprintInfo(blueprint:dict,*,version:bool=False,buildingCount:bool=False,
    size:bool=False,islandCount:bool=False,bpType:bool=False) -> dict[str]:

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

    if buildingCount or size or islandCount or bpType:

        blueprintBP = blueprint.get("BP")

        if blueprintBP is None:
            raise ValueError("No blueprint key")

        if type(blueprintBP) != dict:
            raise ValueError("Blueprint not a dict")

        blueprintBPType = blueprintBP.get("$type")

        if blueprintBPType is None:
            blueprintBPType = "Building"

        if type(blueprintBPType) != str:
            raise ValueError("Blueprint type not a string")

        if blueprintBPType not in ("Building","Island"):
            raise ValueError("Unknown blueprint type")

        islandBP = blueprintBPType == "Island"

        blueprintBPEntries = blueprintBP.get("Entries")

        if blueprintBPEntries is None:
            raise ValueError("No entries key")

        if type(blueprintBPEntries) != list:
            raise ValueError("Entries not a list")

    if bpType:
        toReturn["bpType"] = blueprintBPType

    if islandCount:
        if islandBP:
            toReturn["islandCount"] = len(blueprintBPEntries)
        else:
            toReturn["islandCount"] = 0

    if buildingCount:
        if islandBP:

            toReturnBuildingCount = 0

            for islandEntryIndex,islandEntry in enumerate(blueprintBPEntries):

                if type(islandEntry) != dict:
                    raise ValueError(f"Entry {islandEntryIndex} not a dict")

                entryBuildings = islandEntry.get("B")

                if entryBuildings is None:
                    continue

                if type(entryBuildings) != dict:
                    raise ValueError(f"Buildings entry of island entry {islandEntryIndex} not a dict")

                entryBuildingsType = entryBuildings.get("$type")

                if entryBuildingsType != "Building":
                    raise ValueError(f"Buildings entry type of island entry {islandEntryIndex} not 'Building'")

                entryBuildingsEntries = entryBuildings.get("Entries")

                if type(entryBuildingsEntries) != list:
                    raise ValueError(f"Buildings of island entry {islandEntryIndex} not a list")

                toReturnBuildingCount += len(entryBuildingsEntries)

            toReturn["buildingCount"] = toReturnBuildingCount

        else:
            toReturn["buildingCount"] = len(blueprintBPEntries)

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

            x, y, z = [0 if v is None else v for v in (x,y,z)]

            for value,text in zip((x,y,z),("x","y","z")):
                if type(value) != int:
                    raise ValueError(f"{text} of entry {i} not an int")

            minX, minY, minZ = [specialMin(v1,v2) for v1,v2 in zip((minX,minY,minZ),(x,y,z))]
            maxX, maxY, maxZ = [specialMax(v1,v2) for v1,v2 in zip((maxX,maxY,maxZ),(x,y,z))]

        if minX is None:
            raise ValueError("No valid entries")

        toReturn["size"] = (maxX-minX+1,maxY-minY+1,maxZ-minZ+1)

    return toReturn
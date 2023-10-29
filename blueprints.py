import gzip
import base64
import json

PREFIX = "SHAPEZ2"
SEPARATOR = "-"
SUFFIX = "$"

BUILDING_BP_TYPE = "Building"
ISLAND_BP_TYPE = "Island"

class BlueprintError(Exception): ...

def decodeBlueprint(rawBlueprint:str) -> tuple[dict,int]:
    if rawBlueprint.startswith(PREFIX):
        rawBlueprint = rawBlueprint[len(PREFIX):]
    else:
        raise BlueprintError("doesn't start with prefix")

    if rawBlueprint.startswith(SEPARATOR):
        rawBlueprint = rawBlueprint[len(SEPARATOR):]
    else:
        raise BlueprintError("no separator after prefix")

    rawBlueprint = rawBlueprint.split(SEPARATOR)
    if len(rawBlueprint) == 0:
        raise BlueprintError("nothing after first separator")
    if len(rawBlueprint) == 1:
        raise BlueprintError("no separator after version number")
    if len(rawBlueprint) > 2:
        raise BlueprintError("more separators than expected")

    try:
        majorVersion = int(rawBlueprint[0])
    except ValueError:
        raise BlueprintError("version number not a number")

    rawBlueprint = rawBlueprint[1]
    if rawBlueprint.endswith(SUFFIX):
        rawBlueprint = rawBlueprint[:-len(SUFFIX)]
    else:
        raise BlueprintError("doesn't end with suffix")

    try:
        rawBlueprint = rawBlueprint.encode()
    except Exception:
        raise BlueprintError("can't encode in bytes")
    try:
        rawBlueprint = base64.b64decode(rawBlueprint)
    except Exception:
        raise BlueprintError("can't decode from base64")
    try:
        rawBlueprint = gzip.decompress(rawBlueprint)
    except Exception:
        raise BlueprintError("can't gzip decompress")
    try:
        rawBlueprint = json.loads(rawBlueprint)
    except Exception:
        raise BlueprintError("can't parse json")

    return rawBlueprint, majorVersion

def encodeBlueprint(blueprint:dict,majorVersion:int) -> str:
    try:
        blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint,separators=(",",":")).encode())).decode()
        blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    except Exception:
        raise BlueprintError("error while encoding blueprint")
    return blueprint

def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = decodeBlueprint(blueprint)
    blueprint["V"] = version
    blueprint = encodeBlueprint(blueprint,majorVersion)
    return blueprint

def getBlueprintInfo(blueprint:dict,*,version:bool=False,buildingCount:bool=False,
    size:bool=False,islandCount:bool=False,bpType:bool=False,
    buildingCounts:bool=False,islandCounts:bool=False) -> dict[str]:

    if type(blueprint) != dict:
        raise BlueprintError("Given 'blueprint' argument not a dict")

    toReturn = {}

    if version:

        versionNum = blueprint.get("V")

        if versionNum is None:
            raise BlueprintError("No version key")

        if type(versionNum) != int:
            raise BlueprintError("Version not an int")

        toReturn["version"] = versionNum

    if buildingCount or size or islandCount or bpType or buildingCounts or islandCounts:

        blueprintBP = blueprint.get("BP")

        if blueprintBP is None:
            raise BlueprintError("No blueprint key")

        if type(blueprintBP) != dict:
            raise BlueprintError("Blueprint not a dict")

        blueprintBPType = blueprintBP.get("$type")

        if blueprintBPType is None:
            blueprintBPType = BUILDING_BP_TYPE

        if type(blueprintBPType) != str:
            raise BlueprintError("Blueprint type not a string")

        if blueprintBPType not in (BUILDING_BP_TYPE,ISLAND_BP_TYPE):
            raise BlueprintError("Unknown blueprint type")

        islandBP = blueprintBPType == ISLAND_BP_TYPE

        blueprintBPEntries = blueprintBP.get("Entries")

        if blueprintBPEntries is None:
            raise BlueprintError("No entries key")

        if type(blueprintBPEntries) != list:
            raise BlueprintError("Entries not a list")

    if bpType:
        toReturn["bpType"] = blueprintBPType

    def countsDictAdd(dict_:dict,addToKey:str) -> None:
        if dict_.get(addToKey) is None:
            dict_[addToKey] = 1
        else:
            dict_[addToKey] += 1

    if buildingCount or islandCount or buildingCounts or islandCounts:

        if buildingCount:
            toReturn["buildingCount"] = 0
        if islandCount:
            toReturn["islandCount"] = 0
        if buildingCounts:
            toReturn["buildingCounts"] = {}
        if islandCounts:
            toReturn["islandCounts"] = {}

        for entryIndex,entry in enumerate(blueprintBPEntries):

            if (buildingCounts and (not islandBP)) or (islandCounts and islandBP):

                if type(entry) != dict:
                    raise BlueprintError(f"Entry {entryIndex} not a dict")

                entryType = entry.get("T")

                if entryType is None:
                    raise BlueprintError(f"No type key for entry {entryIndex}")

            if islandBP:

                if islandCount:
                    toReturn["islandCount"] += 1

                if islandCounts:
                    countsDictAdd(toReturn["islandCounts"],entryType)

                if buildingCount or buildingCounts:

                    entryBuildings = entry.get("B")

                    if entryBuildings is None:
                        continue

                    if type(entryBuildings) != dict:
                        raise BlueprintError(f"Buildings entry of island entry {entryIndex} not a dict")

                    entryBuildingsType = entryBuildings.get("$type")

                    if entryBuildingsType != BUILDING_BP_TYPE:
                        raise BlueprintError(f"Buildings entry type of island entry {entryIndex} not '{BUILDING_BP_TYPE}'")

                    entryBuildingsEntries = entryBuildings.get("Entries")

                    if type(entryBuildingsEntries) != list:
                        raise BlueprintError(f"Buildings of island entry {entryIndex} not a list")

                    for buildingEntryIndex,buildingEntry in enumerate(entryBuildingsEntries):

                        if buildingCount:
                            toReturn["buildingCount"] += 1

                        if buildingCounts:

                            if type(buildingEntry) != dict:
                                raise BlueprintError(f"Building entry {buildingEntryIndex} of island entry {entryIndex} not a dict")

                            buildingEntryType = buildingEntry.get("T")

                            if buildingEntryType is None:
                                raise BlueprintError(f"No type key for building entry {buildingEntryIndex} of island entry {entryIndex}")

                            countsDictAdd(toReturn["buildingCounts"],buildingEntryType)

            else:

                if buildingCount:
                    toReturn["buildingCount"] += 1

                if buildingCounts:
                    countsDictAdd(toReturn["buildingCounts"],entryType)

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
                raise BlueprintError(f"Entry {i} not a dict")

            x = entry.get("X")
            y = entry.get("Y")
            z = entry.get("L")

            x, y, z = [0 if v is None else v for v in (x,y,z)]

            for value,text in zip((x,y,z),("x","y","z")):
                if type(value) != int:
                    raise BlueprintError(f"{text} of entry {i} not an int")

            minX, minY, minZ = [specialMin(v1,v2) for v1,v2 in zip((minX,minY,minZ),(x,y,z))]
            maxX, maxY, maxZ = [specialMax(v1,v2) for v1,v2 in zip((maxX,maxY,maxZ),(x,y,z))]

        if minX is None:
            raise BlueprintError("No valid entries")

        toReturn["size"] = (maxX-minX+1,maxY-minY+1,maxZ-minZ+1)

    return toReturn
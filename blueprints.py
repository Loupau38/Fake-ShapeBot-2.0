import utils
from utils import Rotation, Pos, Size
import gameInfos
import gzip
import base64
import json
import typing

PREFIX = "SHAPEZ2"
SEPARATOR = "-"
SUFFIX = "$"

BUILDING_BP_TYPE = "Building"
ISLAND_BP_TYPE = "Island"

NUM_LAYERS = 3
ISLAND_ROTATION_CENTER = utils.FloatPos(*([(gameInfos.islands.ISLAND_SIZE/2)-.5]*2))

class BlueprintError(Exception): ...

class TileEntry:
    def __init__(self,referTo:int) -> None:
        self.referTo = referTo

class BuildingEntry:
    def __init__(self,pos:Pos,rotation:Rotation,type:gameInfos.buildings.Building,extra:bytes) -> None:
        self.pos = pos
        self.rotation = rotation
        self.type = type
        self.extra = extra

    def toJSON(self) -> dict:
        return {
            "X" : self.pos.x,
            "Y" : self.pos.y,
            "L" : self.pos.z,
            "R" : self.rotation.value,
            "T" : self.type.id,
            "C" : base64.b64encode(self.extra).decode()
        }

class BuildingBlueprint:
    def __init__(self,asEntryList:list[BuildingEntry],asTileDict:dict[Pos,TileEntry]) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = asTileDict

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getBuildingCount(self) -> int:
        return len(self.asEntryList)

    def getBuildingCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def toJSON(self) -> dict:
        return {
            "$type" : BUILDING_BP_TYPE,
            "Entries" : [e.toJSON() for e in self.asEntryList]
        }

class IslandEntry:
    def __init__(self,pos:Pos,rotation:Rotation,type:gameInfos.islands.Island,buildingBP:BuildingBlueprint|None) -> None:
        self.pos = pos
        self.rotation = rotation
        self.type = type
        self.buildingBP = buildingBP

    def toJSON(self) -> dict:
        toReturn = {
            "X" : self.pos.x,
            "Y" : self.pos.y,
            "R" : self.rotation.value,
            "T" : self.type.id
        }
        if self.buildingBP is not None:
            toReturn["B"] = self.buildingBP.toJSON()
        return toReturn

class IslandBlueprint:
    def __init__(self,asEntryList:list[IslandEntry],asTileDict:dict[Pos,TileEntry]) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = asTileDict

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getIslandCount(self) -> int:
        return len(self.asEntryList)

    def getIslandCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def toJSON(self) -> dict:
        return {
            "$type" : ISLAND_BP_TYPE,
            "Entries" : [e.toJSON() for e in self.asEntryList]
        }

class Blueprint:
    def __init__(self,majorVersion:int,version:int,type:str,islandBP:IslandBlueprint|None,buildingBP:BuildingBlueprint|None) -> None:
        self.majorVersion = majorVersion
        self.version = version
        self.type = type
        self.islandBP = islandBP
        self.buildingBP = buildingBP

    def toJSON(self) -> tuple[dict,int]:
        return {
            "V" : self.version,
            "BP" : (self.buildingBP if self.islandBP is None else self.islandBP).toJSON()
        }, self.majorVersion

def _genericGetSize(bp:BuildingBlueprint|IslandBlueprint) -> Size:
    (minX,minY,minZ), (maxX,maxY,maxZ) = [[func(e.__dict__[k] for e in bp.asTileDict.keys()) for k in ("x","y","z")] for func in (min,max)]
    return Size(
        maxX - minX + 1,
        maxY - minY + 1,
        maxZ - minZ + 1
    )

def _genericGetCounts(bp:BuildingBlueprint|IslandBlueprint) -> dict[str,int]:
    output = {}
    for entry in bp.asEntryList:
        entryType = entry.type.id
        if output.get(entryType) is None:
            output[entryType] = 1
        else:
            output[entryType] += 1
    return output





_ERR_MSG_PATH_SEP = ">"
_ERR_MSG_PATH_START = "'"
_ERR_MSG_PATH_END = "' : "
_defaultObj = object()

def _getKeyValue(dict:dict,key:str,expectedValueType:type,default:typing.Any=_defaultObj) -> typing.Any:

    value = dict.get(key,_defaultObj)

    if value is _defaultObj:
        if default is _defaultObj:
            raise BlueprintError(f"{_ERR_MSG_PATH_END}Missing '{key}' key")
        return default

    valueType = type(value)
    if valueType != expectedValueType:
        raise BlueprintError(
            f"{_ERR_MSG_PATH_SEP}{key}{_ERR_MSG_PATH_END}Incorrect value type, expected '{expectedValueType.__name__}', got '{valueType.__name__}'")

    return value

def _decodeBlueprintFirstPart(rawBlueprint:str) -> tuple[dict,int]:

    try:

        sepCount = rawBlueprint.count(SEPARATOR)
        if sepCount != 2:
            raise BlueprintError(f"Expected 2 separators, got {sepCount}")

        prefix, majorVersion, codeAndSuffix = rawBlueprint.split(SEPARATOR)

        if prefix != PREFIX:
            raise BlueprintError("Incorrect prefix")

        if not utils.isNumber(majorVersion):
            raise BlueprintError("Version not a number")
        majorVersion = int(majorVersion)

        if codeAndSuffix[-len(SUFFIX):] != SUFFIX:
            raise BlueprintError("Doesn't end with suffix")

        encodedBP = codeAndSuffix[:-len(SUFFIX)]

        if encodedBP == "":
            raise BlueprintError("Empty encoded section")

        try:
            encodedBP = encodedBP.encode()
        except Exception:
            raise BlueprintError("Can't encode in bytes")
        try:
            encodedBP = base64.b64decode(encodedBP)
        except Exception:
            raise BlueprintError("Can't decode from base64")
        try:
            encodedBP = gzip.decompress(encodedBP)
        except Exception:
            raise BlueprintError("Can't gzip decompress")
        try:
            decodedBP = json.loads(encodedBP)
        except Exception:
            raise BlueprintError("Can't parse json")

        try:
            _getKeyValue(decodedBP,"V",int)
            _getKeyValue(decodedBP,"BP",dict)
        except BlueprintError as e:
            raise BlueprintError(f"Error in {_ERR_MSG_PATH_START}blueprint json object{e}")

    except BlueprintError as e:
        raise BlueprintError(f"Error while decoding blueprint string : {e}")

    return decodedBP, majorVersion

def _encodeBlueprintLastPart(blueprint:dict,majorVersion:int) -> str:
    try:
        blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint,indent=4).encode())).decode()
        blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    except Exception:
        raise BlueprintError("Error while encoding blueprint")
    return blueprint

def _getValidBlueprint(blueprint:dict,mustBeBuildingBP:bool=False) -> dict:

    validBP = {}

    bpType = _getKeyValue(blueprint,"$type",str,BUILDING_BP_TYPE)

    if bpType not in (BUILDING_BP_TYPE,ISLAND_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Unknown blueprint type : '{bpType}'")

    if mustBeBuildingBP and (bpType != BUILDING_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Must be a building blueprint")

    validBP["$type"] = bpType

    allowedEntryTypes = (
        gameInfos.buildings.allBuildings.keys()
        if bpType == BUILDING_BP_TYPE else
        gameInfos.islands.allIslands.keys()
    )

    bpEntries = _getKeyValue(blueprint,"Entries",list)

    if bpEntries == []:
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Entries{_ERR_MSG_PATH_END}Empty list")

    validBPEntries = []

    for i,entry in enumerate(bpEntries):
        try:

            entryType = type(entry)
            if entryType != dict:
                raise BlueprintError(f"{_ERR_MSG_PATH_END}Incorrect value type, expected 'dict', got '{entryType.__name__}'")

            x, y, l, r = (_getKeyValue(entry,k,int,0) for k in ("X","Y","L","R"))

            if (r < 0) or (r > 3):
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}R{_ERR_MSG_PATH_END}Rotation must be in range from 0 to 3")

            t = _getKeyValue(entry,"T",str)

            if t not in allowedEntryTypes:
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}T{_ERR_MSG_PATH_END}Unknown entry type '{t}'")

            validEntry = {
                "X" : x,
                "Y" : y,
                "L" : l,
                "R" : r,
                "T" : t
            }

            if bpType == ISLAND_BP_TYPE:
                b = entry.get("B",_defaultObj)
                if b is not _defaultObj:
                    b = _getKeyValue(entry,"B",dict)
                    try:
                        validB = _getValidBlueprint(b,True)
                    except BlueprintError as e:
                        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}B{e}")
                    validEntry["B"] = validB
            else:
                c = _getKeyValue(entry,"C",str,"")
                try:
                    c = base64.b64decode(c)
                except Exception:
                    raise BlueprintError(f"{_ERR_MSG_PATH_SEP}C{_ERR_MSG_PATH_END}Can't decode from base64")
                validEntry["C"] = c

            validBPEntries.append(validEntry)

        except BlueprintError as e:
            raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Entries{_ERR_MSG_PATH_SEP}{i}{e}")

    validBP["Entries"] = validBPEntries

    return validBP

def _decodeBuildingBP(buildings:list[dict[str,int|str|bytes]],moveBPCenter:bool=True) -> BuildingBlueprint:

    tileDict:dict[Pos,TileEntry] = {}
    entryList:list[BuildingEntry] = []

    for buildingIndex,building in enumerate(buildings):

        curTiles = [t.rotateCW(building["R"]) for t in gameInfos.buildings.allBuildings[building["T"]].tiles]
        curTiles = [Pos(building["X"]+t.x,building["Y"]+t.y,building["L"]+t.z) for t in curTiles]

        for curTile in curTiles:

            if tileDict.get(curTile) is not None:
                raise BlueprintError(f"Error while placing tile of '{building['T']}' at {curTile} : another tile is already placed there")

            tileDict[curTile] = TileEntry(buildingIndex)

    minX, minY, minZ = [min(e.__dict__[k] for e in tileDict.keys()) for k in ("x","y","z")]
    maxZ = max(e.z for e in tileDict.keys())

    if maxZ-minZ+1 > NUM_LAYERS:
        raise BlueprintError(f"Cannot have more than {NUM_LAYERS} layers")

    if moveBPCenter:
        tileDict = {Pos(p.x-minX,p.y-minY,p.z-minZ) : t for p,t in tileDict.items()}

    for b in buildings:
        if moveBPCenter:
            b["X"] -= minX
            b["Y"] -= minY
            b["L"] -= minZ
        entryList.append(BuildingEntry(Pos(
            b["X"],b["Y"],b["L"]),
            b["R"],
            gameInfos.buildings.allBuildings[b["T"]],
            b["C"]
        ))

    return BuildingBlueprint(entryList,tileDict)

def _decodeIslandBP(islands:list[dict[str,int|str|dict]]) -> tuple[IslandBlueprint,BuildingBlueprint|None]:

    tileDict:dict[Pos,TileEntry] = {}
    entryList:list[IslandEntry] = []

    for islandIndex,island in enumerate(islands):

        curTiles = [t.pos.rotateCW(island["R"]) for t in gameInfos.islands.allIslands[island["T"]].tiles]
        curTiles = [Pos(island["X"]+t.x,island["Y"]+t.y) for t in curTiles]

        for curTile in curTiles:

            if tileDict.get(curTile) is not None:
                raise BlueprintError(f"Error while placing tile of '{island['T']}' at {curTile} : another tile is already placed there")

            tileDict[curTile] = TileEntry(islandIndex)

    minX, minY = [min(e.__dict__[k] for e in tileDict.keys()) for k in ("x","y")]

    tileDict = {Pos(p.x-minX,p.y-minY) : t for p,t in tileDict.items()}

    for i in islands:
        i["X"] -= minX
        i["Y"] -= minY

    globalBuildingList:list[BuildingEntry] = []
    globalBuildingDict:dict[Pos,TileEntry] = {}

    for island in islands:

        if island.get("B") is None:
            entryList.append(IslandEntry(
                Pos(island["X"],island["Y"]),
                island["R"],
                gameInfos.islands.allIslands[island["T"]],
                None
            ))
            continue

        try:
            curBuildingBP = _decodeBuildingBP(island["B"]["Entries"],False)
        except BlueprintError as e:
            raise BlueprintError(
                f"Error while creating representation of building blueprint of '{island['T']}' at {Pos(island['X'],island['Y'])} : {e}")

        curIslandBuildArea = [a.rotateCW(island["R"],ISLAND_ROTATION_CENTER) for a in gameInfos.islands.allIslands[island["T"]].totalBuildArea]

        for pos,b in curBuildingBP.asTileDict.items():

            curBuilding = curBuildingBP.asEntryList[b.referTo]

            inArea = False
            for area in curIslandBuildArea:
                if area.containsPos(pos):
                    inArea = True
                    break
            if not inArea:
                raise BlueprintError(
                    f"Error in island '{island['T']}' at {Pos(island['X'],island['Y'])} : tile of building '{curBuilding.type.id}' at {pos} is not inside it's island build area")

            globalBuildingDict[
                Pos(
                    (island["X"]*gameInfos.islands.ISLAND_SIZE) + curBuilding.pos.x,
                    (island["Y"]*gameInfos.islands.ISLAND_SIZE) + curBuilding.pos.y,
                    curBuilding.pos.z
                )
            ] = TileEntry(len(globalBuildingList)+b.referTo)

        for b in curBuildingBP.asEntryList:
            globalBuildingList.append(BuildingEntry(
                Pos(
                    (island["X"]*gameInfos.islands.ISLAND_SIZE) + b.pos.x,
                    (island["Y"]*gameInfos.islands.ISLAND_SIZE) + b.pos.y,
                    b.pos.z
                ),
                b.rotation,
                b.type,
                b.extra
            ))

        entryList.append(IslandEntry(
            Pos(island["X"],island["Y"]),
            island["R"],
            gameInfos.islands.allIslands[island["T"]],
            curBuildingBP
        ))

    return IslandBlueprint(entryList,tileDict), (BuildingBlueprint(globalBuildingList,globalBuildingDict) if globalBuildingList != [] else None)



def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = _decodeBlueprintFirstPart(blueprint)
    blueprint["V"] = version
    blueprint = _encodeBlueprintLastPart(blueprint,majorVersion)
    return blueprint

def getBlueprintVersion(blueprint:str) -> int:
    return _decodeBlueprintFirstPart(blueprint)[0]["V"]

def decodeBlueprint(rawBlueprint:str) -> Blueprint:
    decodedBP, majorVersion = _decodeBlueprintFirstPart(rawBlueprint)
    version = decodedBP["V"]

    try:
        validBP = _getValidBlueprint(decodedBP["BP"])
    except BlueprintError as e:
        raise BlueprintError(f"Error in {_ERR_MSG_PATH_START}blueprint json object{_ERR_MSG_PATH_SEP}BP{e}")

    bpType = validBP["$type"]

    if bpType == BUILDING_BP_TYPE:
        try:
            buildingBP = _decodeBuildingBP(validBP["Entries"])
        except BlueprintError as e:
            raise BlueprintError(f"Error while creating building blueprint representation : {e}")
        return Blueprint(majorVersion,version,bpType,None,buildingBP)

    try:
        islandBP, buildingBP = _decodeIslandBP(validBP["Entries"])
    except BlueprintError as e:
        raise BlueprintError(f"Error while creating island blueprint representation : {e}")
    return Blueprint(majorVersion,version,bpType,islandBP,buildingBP)

def encodeBlueprint(blueprint:Blueprint) -> str:
    try:
        encodedBP, majorVersion = blueprint.toJSON()
    except Exception:
        raise BlueprintError("Error while encoding blueprint")
    return _encodeBlueprintLastPart(encodedBP,majorVersion)

def getPotentialBPCodesInString(string:str) -> list[str]:

    if PREFIX not in string:
        return []

    bps = string.split(PREFIX)[1:]

    bpCodes = []

    for bp in bps:

        if SUFFIX not in bp:
            continue

        bp = bp.split(SUFFIX)[0]

        bpCodes.append(PREFIX+bp+SUFFIX)

    return bpCodes
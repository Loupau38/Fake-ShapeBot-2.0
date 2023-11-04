import blueprints
import globalInfos
import bot
import typing

def detectBPVersion(message:str) -> list[str]|None:

    if blueprints.PREFIX not in message:
        return None

    bps = message.split(blueprints.PREFIX)[1:]

    versions = []

    for bp in bps:

        if blueprints.SUFFIX not in bp:
            continue

        bp = bp.split(blueprints.SUFFIX)[0]

        try:
            bp,_ = blueprints.decodeBlueprint(blueprints.PREFIX+bp+blueprints.SUFFIX)
        except blueprints.BlueprintError:
            continue

        try:
            version = blueprints.getBlueprintInfo(bp,version=True)["version"]
        except blueprints.BlueprintError:
            continue

        versionReaction = bot.convertVersionNum(version,toReaction=True)

        if versionReaction is None:
            continue

        versions.append(versionReaction)

    if len(versions) != 1:
        return None

    return versions[0]

def handleMsgTooLong(msg:str) -> str:
    if len(msg) > globalInfos.MESSAGE_MAX_LENGTH:
        return globalInfos.MESSAGE_TOO_LONG_TEXT
    return msg

class OutputString:

    class Number:
        def __init__(self,num:int|float,isIndex:bool=False) -> None:
            self.num = num
            self.isIndex = isIndex

    class UnsafeString:
        def __init__(self,string:str) -> None:
            self.string = string

    class UnsafeNumber:
        def __init__(self,num:int|float,isIndex:bool=False) -> None:
            self.num = num
            self.isIndex = isIndex

    def __init__(self,*elems:str|Number|UnsafeString|UnsafeNumber|typing.Self) -> None:
        self.elems = list(elems)

    def render(self,isShownPublicly:bool) -> str:

        output = ""
        for elem in self.elems:
            elemType = type(elem)

            if elemType == str:
                output += elem

            elif elemType == OutputString.UnsafeString:
                if isShownPublicly:
                    output += f"<{len(elem.string)} character(s) long string not shown because public>"
                else:
                    output += elem.string

            elif elemType == OutputString.Number:
                output += str(elem.num + (1 if elem.isIndex else 0))

            elif elemType == OutputString.UnsafeNumber:
                output += str(elem.num + (1 if elem.isIndex else 0))

            elif elemType == OutputString:
                output += elem.render(isShownPublicly)

            else:
                raise TypeError(f"Unknown elem type in OutputString.elems while executing 'render' function : {elemType.__name__}")

        return output
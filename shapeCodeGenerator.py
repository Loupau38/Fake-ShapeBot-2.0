import math
COLOR_SHAPES = ["C","R","S","W"]
NO_COLOR_SHAPES = ["P","c"]
COLORS = ["u","r","g","b","c","p","y","w","k"]
NOTHING_CHAR = "-"
COLOR_SHAPES_DEFAULT_COLOR = COLORS[0]
NO_COLOR_SHAPES_DEFAULT_COLOR = NOTHING_CHAR
LAYER_SEPARATOR = ":"
PARAM_PREFIX = "+"
DISPLAY_PARAM_PREFIX = "/"
DISPLAY_PARAM_EXIT_CHAR = " "
DISPLAY_PARAM_KEY_VALUE_SEPARATOR = ":"
SHAPE_CODE_OPENING = "{"
SHAPE_CODE_CLOSING = "}"
INGNORE_CHARS_IN_SHAPE_CODE = ["`"]
LEVEL_SHAPE_PREFIXES = ["level","lvl","m"]
LEVEL_SHAPES = ["CuCuCuCu","----RuRu","Cu------","CuCuRuRu","CuCuCuRu",
    "Cu----Ru","CuRuCuRu:Cu--Cu--","SuSuSuSu","WuCuWuCu:CuCuCuCu","RrCrRrCr",
    "SgCrCrSg:--CuCu--","SgCrCrSg:CbCbCbCb","RuCrP-Cr:----Ru--","RgCrP-Cr:P-P-RgP-:CbCb--Cb","RuCwP-Cw:----Ru--",
    "CwCrCwCr:CrCwCrCw:CwCrCwCr:CrCwCrCw","Cuc-Cuc-","P-"]
def getPotentialShapeCodesFromMessage(message:str) -> list[str]:
    if (message == "") or (SHAPE_CODE_OPENING not in message):
        return []
    openingSplits = message.split(SHAPE_CODE_OPENING)
    potentialShapeCodes = []
    for split in openingSplits:
        if SHAPE_CODE_CLOSING in split:
            potentialShapeCode = split.split(SHAPE_CODE_CLOSING)[0]
            if potentialShapeCode != "":
                potentialShapeCodes.append(potentialShapeCode)
    return potentialShapeCodes
def getPotentialDisplayParamsFromMessage(message:str) -> list[tuple]:
    if (message == "") or (DISPLAY_PARAM_PREFIX not in message):
        return []
    prefixSplits = message.split(DISPLAY_PARAM_PREFIX)
    potentialDisplayParams = []
    for split in prefixSplits:
        if DISPLAY_PARAM_EXIT_CHAR in split:
            potentialDisplayParam = split.split(DISPLAY_PARAM_EXIT_CHAR)[0]
        else:
            potentialDisplayParam = split
        if DISPLAY_PARAM_KEY_VALUE_SEPARATOR in potentialDisplayParam:
            potentialDisplayParams.append(tuple(potentialDisplayParam.split(DISPLAY_PARAM_KEY_VALUE_SEPARATOR)[:2]))
        else:
            potentialDisplayParams.append((potentialDisplayParam,))
    return potentialDisplayParams
def generateShapeCodes(potentialShapeCode:str) -> tuple[list[str]|str,bool]:
    """Returns (``[shapeCode0,shapeCode1,...]`` or ``errorMsg``), ``isShapeCodeValid``"""
    for char in INGNORE_CHARS_IN_SHAPE_CODE:
        potentialShapeCode = potentialShapeCode.replace(char,"")
    if PARAM_PREFIX in potentialShapeCode:
        params = potentialShapeCode.split(PARAM_PREFIX)
        potentialShapeCode = params[0]
        params = params[1:]
    else:
        params = []
    cutInParams = "cut" in params
    qcutInParams = "qcut" in params
    if cutInParams and qcutInParams:
        return "Mutualy exclusive 'cut' and 'qcut' parameters present",False
    # handle level/milestone shapes
    for prefix in LEVEL_SHAPE_PREFIXES:
        if potentialShapeCode.startswith(prefix):
            invalidLvl = False
            level = potentialShapeCode[len(prefix):]
            try:
                level = int(level)
                if (level < 1) or (level > len(LEVEL_SHAPES)):
                    invalidLvl = True
            except ValueError:
                invalidLvl = True
            if invalidLvl:
                return f"Invalid level/milestone number : '{level}'",False
            potentialShapeCode = LEVEL_SHAPES[level-1]
            break
    # separate in layers
    if LAYER_SEPARATOR in potentialShapeCode:
        layers = potentialShapeCode.split(LAYER_SEPARATOR)
        for i,layer in enumerate(layers):
            if layer == "":
                return f"Layer {i+1} empty",False
    else:
        if potentialShapeCode == "":
            return "Empty shape code",False
        layers = [potentialShapeCode]
    # handle lfill
    if "lfill" in params:
        layersLen = len(layers)
        if layersLen == 1:
            layers = [layers[0]]*4
        elif layersLen == 2:
            layers = [layers[0],layers[1]]*2
    # handle struct
    if "struct" in params:
        for i,layer in enumerate(layers):
            for char in layer:
                if char not in ("0","1"):
                    return f"Use of 'struct' parameter but layer {i+1} doesn't contain only '0' or '1'",False
        for i,layer in enumerate(layers):
            newLayer = ""
            if i > 2:
                color = "w"
            else:
                color = ["r","g","b"][i]
            for char in layer:
                newLayer += f"C{color}" if char == "1" else NOTHING_CHAR*2
            layers[i] = newLayer
    # change magenta to purple
    for layerIndex,layer in enumerate(layers):
        layers[layerIndex] = layer.replace("m","p")
    # verify if only valid chars
    for layerIndex,layer in enumerate(layers):
        for charIndex,char in enumerate(layer):
            if char not in [*COLOR_SHAPES,*NO_COLOR_SHAPES,*COLORS,NOTHING_CHAR]:
                return f"Invalid char in layer {layerIndex+1} ({layer}), at char {charIndex+1} : '{char}'",False
    # handle {C} -> {Cu} transformation
    for layerIndex,layer in enumerate(layers):
        newLayer = ""
        lastChar = len(layer)-1
        skipNext = False
        for charIndex,char in enumerate(layer):
            if skipNext:
                newLayer += char
                skipNext = False
                continue
            expand = False
            isLastChar = charIndex == lastChar
            if (char in COLOR_SHAPES) and ((isLastChar) or (layer[charIndex+1] not in COLORS)):
                expand = True
            elif (char in [*NO_COLOR_SHAPES,NOTHING_CHAR]) and ((isLastChar) or (layer[charIndex+1] != NOTHING_CHAR)):
                expand = True
            if expand:
                if char in [*NO_COLOR_SHAPES,NOTHING_CHAR]:
                    newLayer += char+NO_COLOR_SHAPES_DEFAULT_COLOR
                else:
                    newLayer += char+COLOR_SHAPES_DEFAULT_COLOR
            else:
                skipNext = True
                newLayer += char
        layers[layerIndex] = newLayer
    # verify if shapes and colors are in the right positions
    for layerIndex,layer in enumerate(layers):
        shapeMode = True
        lastChar = len(layer)-1
        for charIndex,char in enumerate(layer):
            errorMsgStart = f"Char in layer {layerIndex+1} ({layer}) at char {charIndex+1} ({char})"
            if shapeMode:
                if char not in [*COLOR_SHAPES,*NO_COLOR_SHAPES,NOTHING_CHAR]:
                    return f"{errorMsgStart} must be a shape or empty",False
                if charIndex == lastChar:
                    return f"{errorMsgStart} should have a color but is end of layer",False
                if char in [*NO_COLOR_SHAPES,NOTHING_CHAR]:
                    nextMustBeColor = False
                else:
                    nextMustBeColor = True
                shapeMode = False
            else:
                if char not in [*COLORS,NOTHING_CHAR]:
                    return f"{errorMsgStart} must be a color or empty",False
                if nextMustBeColor and (char not in COLORS):
                    return f"{errorMsgStart} must be a color",False
                if (not nextMustBeColor) and (char != NOTHING_CHAR):
                    return f"{errorMsgStart} must be empty"
                shapeMode = True
    # handle fill
    if "fill" in params:
        for layerIndex,layer in enumerate(layers):
            newLayer = ""
            layerLen = len(layer)
            if layerLen == 2:
                newLayer = layer*4
            elif layerLen == 4:
                newLayer = layer*2
            else:
                newLayer = layer
            layers[layerIndex] = newLayer
    expectedLayerLen = len(layers[0])
    for layerIndex,layer in enumerate(layers[1:]):
        if len(layer) != expectedLayerLen:
            return f"Layer {layerIndex+2} ({layer}){f' (or 1 ({layers[0]}))' if layerIndex == 0 else ''} doesn't have the expected number of quadrants",False
    if "lsep" in params:
        shapeCodes = [[layer] for layer in layers]
    else:
        shapeCodes = [layers]
    #handle cut
    if cutInParams:
        newShapeCodes = []
        for shape in shapeCodes:
            numQuads = round(len(shape[0])/2)
            takeQuads = math.ceil(numQuads/2)
            shape1 = []
            shape2 = []
            for layer in shape:
                shape1.append(f"{NOTHING_CHAR*((numQuads-takeQuads)*2)}{layer[:takeQuads*2]}")
                shape2.append(f"{layer[takeQuads*2:]}{NOTHING_CHAR*(takeQuads*2)}")
            newShapeCodes.extend([shape1,shape2])
    #handle qcut
    elif qcutInParams:
        newShapeCodes = []
        for shape in shapeCodes:
            numQuads = round(len(shape[0])/2)
            takeQuads = math.ceil(numQuads/2)
            takeQuads1 = math.ceil(takeQuads/2)
            takeQuads2 = takeQuads - takeQuads1
            takeQuads3 = math.ceil((numQuads-takeQuads)/2)
            takeQuads4 = numQuads - takeQuads - takeQuads3
            shape1 = []
            shape2 = []
            shape3 = []
            shape4 = []
            for layer in shape:
                shape1.append(f"{layer[:takeQuads1*2]}{NOTHING_CHAR*((takeQuads2+takeQuads3+takeQuads4)*2)}")
                shape2.append(f"{NOTHING_CHAR*(takeQuads1*2)}{layer[takeQuads1*2:(takeQuads1+takeQuads2)*2]}{NOTHING_CHAR*((takeQuads3+takeQuads4)*2)}")
                shape3.append(f"{NOTHING_CHAR*((takeQuads1+takeQuads2)*2)}{layer[(takeQuads1+takeQuads2)*2:(takeQuads1+takeQuads2+takeQuads3)*2]}{NOTHING_CHAR*(takeQuads4*2)}")
                shape4.append(f"{NOTHING_CHAR*((takeQuads1+takeQuads2+takeQuads3)*2)}{layer[(takeQuads1+takeQuads2+takeQuads3)*2:]}")
            newShapeCodes.extend([shape1,shape2,shape3,shape4])
    else:
        newShapeCodes = shapeCodes
    noEmptyShapeCodes = []
    for shape in newShapeCodes:
        if any((char != NOTHING_CHAR) for char in ("".join(shape))):
            noEmptyShapeCodes.append(":".join(shape))
    return noEmptyShapeCodes,True
# if __name__ == "__main__":
#     from loupauTools import pygameTools
#     import pygame
#     pygameTools.init()
#     message = "{SrRgCbWc:WpCyRkSw:c-P-CuP-}/size:100"
#     potentialShapeCodes = getPotentialShapeCodesFromMessage(message)
#     if potentialShapeCodes == []:
#         print("do nothing")
#     else:
#         shapeCodes = []
#         for i,code in enumerate(potentialShapeCodes):
#             shapeCodesOrError, isShapeCodeValid = generateShapeCodes(code)
#             if isShapeCodeValid:
#                 shapeCodes.extend(shapeCodesOrError)
#             else:
#                 print(f"Invalid shape code for shape {i} : {shapeCodesOrError}")
#         if shapeCodes == []:
#             print("do nothing")
#         else:
#             potentialDisplayParams = getPotentialDisplayParamsFromMessage(message)
#             spoiler = False
#             size = 56
#             for param in potentialDisplayParams:
#                 if param[0] == "spoiler":
#                     spoiler = True
#                 elif param[0] == "size":
#                     try:
#                         size = min(100,max(10,int(param[1])))
#                     except ValueError:
#                         pass
#             print(f"{spoiler=}")
#             print(f"{size=}")
#             for code in shapeCodes:
#                 surface = pygame.Surface((500,500))
#                 surface.fill((49,51,56))
#                 renderedShape = shapeViewer.renderShape(code,size)
#                 surface.blit(renderedShape,(250-(size/2),250-(size/2)))
#                 pygameTools.displaySurface(surface)
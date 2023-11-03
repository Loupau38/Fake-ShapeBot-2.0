import shapeCodeGenerator
import shapeViewer
import globalInfos
import pygame
import io

class DisplayParam:

    def __init__(self,type:str,default,*,rangeStart:int|None=None,rangeStop:int|None=None) -> None:
        self.type = type
        self.default = default
        if type == "int":
            self.rangeStart = rangeStart
            self.rangeStop = rangeStop

    def getValidValue(self,inputValue:tuple[str]|tuple[str,str]) -> bool|int|None:
        if self.type == "bool":
            return True
        try:
            return min(self.rangeStop,max(self.rangeStart,int(inputValue[1])))
        except IndexError:
            pass
        except ValueError:
            pass

DISPLAY_PARAMS:dict[str,DisplayParam] = {
    "spoiler" : DisplayParam("bool",False),
    "size" : DisplayParam("int",
        globalInfos.DEFAULT_SHAPE_SIZE,
        rangeStart=globalInfos.MIN_SHAPE_SIZE,
        rangeStop=globalInfos.MAX_SHAPE_SIZE),
    "result" : DisplayParam("bool",False),
    "3d" : DisplayParam("bool",False)
}

def handleResponse(message:str) -> None|tuple[None|tuple[tuple[io.BytesIO,int],bool,None|list[str],None|list[str]],bool,list[str]]:

    potentialShapeCodes = shapeCodeGenerator.getPotentialShapeCodesFromMessage(message)

    if potentialShapeCodes == []:
        return

    shapeCodes:list[str] = []
    hasAtLeastOneInvalidShapeCode = False
    errorMsgs = []

    for i,code in enumerate(potentialShapeCodes):
        shapeCodesOrError, isShapeCodeValid = shapeCodeGenerator.generateShapeCodes(code)
        if isShapeCodeValid:
            shapeCodes.extend(shapeCodesOrError)
        else:
            errorMsgs.append(f"Invalid shape code for shape {i+1} : {shapeCodesOrError}")
            hasAtLeastOneInvalidShapeCode = True

    if shapeCodes == []:
        return None,hasAtLeastOneInvalidShapeCode,errorMsgs

    potentialDisplayParams = shapeCodeGenerator.getPotentialDisplayParamsFromMessage(message)
    curDisplayParams = {k:v.default for k,v in DISPLAY_PARAMS.items()}

    for param in potentialDisplayParams:
        if DISPLAY_PARAMS.get(param[0]) is not None:
            tempValue = DISPLAY_PARAMS[param[0]].getValidValue(param)
            if tempValue is not None:
                curDisplayParams[param[0]] = tempValue

    numShapes = len(shapeCodes)
    size = curDisplayParams["size"]
    finalImage = pygame.Surface(
        (size*min(globalInfos.SHAPES_PER_ROW,numShapes),size*(((numShapes-1)//globalInfos.SHAPES_PER_ROW)+1)),
        pygame.SRCALPHA)

    renderedShapesCache = {}
    for i,code in enumerate(shapeCodes):
        if renderedShapesCache.get(code) is None:
            renderedShapesCache[code] = shapeViewer.renderShape(code,size)
        divMod = divmod(i,globalInfos.SHAPES_PER_ROW)
        finalImage.blit(renderedShapesCache[code],(size*divMod[1],size*divMod[0]))

    viewer3dLinks = None
    if curDisplayParams["3d"]:
        viewer3dLinks = []
        for code in shapeCodes:
            link = f"<{globalInfos.VIEWER_3D_LINK_START}{code}>"
            for old,new in globalInfos.VIEWER_3D_CHAR_REPLACEMENT.items():
                link.replace(old,new)
            viewer3dLinks.append(link)

    with io.BytesIO() as buffer:
        pygame.image.save(finalImage,buffer,"png")
        bufferValue = buffer.getvalue()
        finalImageBytesLen = len(bufferValue)
        finalImageBytes = io.BytesIO(bufferValue)

    return (
        (
            (finalImageBytes,finalImageBytesLen),
            curDisplayParams["spoiler"],
            shapeCodes if curDisplayParams["result"] else None,
            viewer3dLinks
        ),
        hasAtLeastOneInvalidShapeCode,
        errorMsgs
    )
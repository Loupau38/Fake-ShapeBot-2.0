import shapeCodeGenerator
import shapeViewer
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os
import pygame
import globalInfos
import io
def handleResponse(message:str) -> None|tuple[None|tuple[io.BytesIO,bool,None|list[str]],bool,list[str]]:
    potentialShapeCodes = shapeCodeGenerator.getPotentialShapeCodesFromMessage(message)
    if potentialShapeCodes == []:
        return
    else:
        shapeCodes = []
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
        else:
            potentialDisplayParams = shapeCodeGenerator.getPotentialDisplayParamsFromMessage(message)
            spoiler = globalInfos.DISPLAY_PARAMS_DEFAULT["spoiler"]
            size = globalInfos.DISPLAY_PARAMS_DEFAULT["size"]
            showResult = globalInfos.DISPLAY_PARAMS_DEFAULT["result"]
            for param in potentialDisplayParams:
                if param[0] == "spoiler":
                    spoiler = True
                elif param[0] == "size":
                    try:
                        size = min(globalInfos.MAX_SHAPE_SIZE,max(globalInfos.MIN_SHAPE_SIZE,int(param[1])))
                    except ValueError:
                        pass
                elif param[0] == "result":
                    showResult = True
            numShapes = len(shapeCodes)
            finalImage = pygame.Surface(
                (size*min(globalInfos.SHAPES_PER_ROW,numShapes),size*(((numShapes-1)//globalInfos.SHAPES_PER_ROW)+1)),
                pygame.SRCALPHA)
            for i,code in enumerate(shapeCodes):
                renderedShape = shapeViewer.renderShape(code,size)
                divMod = divmod(i,globalInfos.SHAPES_PER_ROW)
                finalImage.blit(renderedShape,(size*divMod[1],size*divMod[0]))
            with io.BytesIO() as buffer:
                pygame.image.save(finalImage,buffer,"png")
                return (
                    (
                        io.BytesIO(buffer.getvalue()),
                        spoiler,
                        shapeCodes if showResult else None
                    ),
                    hasAtLeastOneInvalidShapeCode,
                    errorMsgs
                )
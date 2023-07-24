import shapeCodeGenerator
import shapeViewer
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os
import pygame
import globalInfos
import io
def handleResponse(message:str) -> str|None:
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
                errorMsgs.append(f"Invalid shape code for shape {i} : {shapeCodesOrError}")
                hasAtLeastOneInvalidShapeCode = True
        if shapeCodes == []:
            return None,hasAtLeastOneInvalidShapeCode,errorMsgs
        else:
            potentialDisplayParams = shapeCodeGenerator.getPotentialDisplayParamsFromMessage(message)
            spoiler = False
            size = 56
            for param in potentialDisplayParams:
                if param[0] == "spoiler":
                    spoiler = True
                elif param[0] == "size":
                    try:
                        size = min(globalInfos.MAX_SHAPE_SIZE,max(globalInfos.MIN_SHAPE_SIZE,int(param[1])))
                    except ValueError:
                        pass
            numShapes = len(shapeCodes)
            finalImage = pygame.Surface(
                (size*min(globalInfos.SHAPES_PER_ROW,numShapes),size*(((numShapes-1)//globalInfos.SHAPES_PER_ROW)+1)),
                pygame.SRCALPHA)
            for i,code in enumerate(shapeCodes):
                renderedShape = shapeViewer.renderShape(code,size)
                divMod = divmod(i,globalInfos.SHAPES_PER_ROW)
                finalImage.blit(renderedShape,(size*divMod[1],size*divMod[0]))
            pygame.image.save(finalImage,globalInfos.IMAGE_PATH)
            return (globalInfos.IMAGE_PATH,spoiler),hasAtLeastOneInvalidShapeCode,errorMsgs
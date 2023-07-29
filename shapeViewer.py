import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os
import pygame
import globalInfos
LAYER_SIZE_REDUCTION = 0.70 # maybe it should be 0.76, maybe not
COLORS = {
    "u":(187,187,186),
    "r":(255,0,0),
    "g":(0,255,0),
    "b":(0,0,255),
    "c":(0,255,255),
    "p":(255,0,255),
    "y":(255,255,0),
    "w":(255,255,255),
    "k":(0,0,0)
}
SHAPE_BORDER_COLOR = (0,0,0)
BG_CIRCLE_COLOR = (31,41,61,25)
DEFAULT_IMAGE_SIZE = 602
DEFAULT_BG_CIRCLE_DIAMETER = 520
DEFAULT_SHAPE_DIAMETER = 422
DEFAULT_BORDER_SIZE = 25 # should be 15, artificially increased to look better
def renderShape(shapeCode:str,surfaceSize:int) -> pygame.Surface:
    fakeSurfaceSize = globalInfos.INITIAL_SHAPE_SIZE
    shapeSize = (fakeSurfaceSize*DEFAULT_SHAPE_DIAMETER)/DEFAULT_IMAGE_SIZE
    shapeBorderSize = round((fakeSurfaceSize*DEFAULT_BORDER_SIZE)/DEFAULT_IMAGE_SIZE)
    bgCircleDiameter = (fakeSurfaceSize*DEFAULT_BG_CIRCLE_DIAMETER)/DEFAULT_IMAGE_SIZE
    shapeSizeOn2 = shapeSize/2
    shapesShape = {
        "C" : {
            "type" : "circle",
            "pos" : (0,shapeSizeOn2,shapeSizeOn2)
        },
        "R" : {
            "type" : "rect",
            "pos" : (0,0,shapeSizeOn2,shapeSizeOn2)
        },
        "S" : {
            "type" : "polygon",
            "points" : [(shapeSizeOn2,0),(shapeSize/4,shapeSizeOn2),(0,shapeSizeOn2),(0,shapeSize/4)]
        },
        "W" : {
            "type" : "polygon",
            "points" : [(0,0),(shapeSizeOn2,0),(shapeSize/4,shapeSizeOn2),(0,shapeSizeOn2)]
        },
        "P" : {
            "type" : "circle",
            "pos" : (shapeSize/6,shapeSize/3,shapeSize/12),
            "color" : (68,68,80),
            "border" : False
        },
        "c" : {
            "type" : "circle",
            "pos" : (0,shapeSizeOn2,shapeSizeOn2),
            "color" : (50,160,180),
            "border" : False
        }
    }
    decomposedShapeCode = shapeCode.split(":")
    numQuads = int(len(decomposedShapeCode[0])/2)
    decomposedShapeCode = [[(layer[i*2],layer[(i*2)+1]) for i in range(numQuads)] for layer in decomposedShapeCode]
    returnSurface = pygame.Surface((fakeSurfaceSize,fakeSurfaceSize),pygame.SRCALPHA)
    pygame.draw.circle(returnSurface,BG_CIRCLE_COLOR,(fakeSurfaceSize/2,fakeSurfaceSize/2),bgCircleDiameter/2)
    for layerIndex, layer in enumerate(decomposedShapeCode):
        for quadIndex, quad in enumerate(layer):
            quadShape = quad[0]
            quadColor = quad[1]
            if quadShape == "-":
                continue
            quadSurface = pygame.Surface((shapeSizeOn2,shapeSizeOn2),flags=pygame.SRCALPHA)
            shapeShape = shapesShape[quadShape]
            tempColor = shapeShape.get("color")
            if tempColor is None:
                tempColor = COLORS[quadColor]
            if shapeShape["type"] == "circle":
                pygame.draw.circle(quadSurface,tempColor,
                    (shapeShape["pos"][0],shapeShape["pos"][1]),shapeShape["pos"][2])
                if shapeShape.get("border") is not False:
                    pygame.draw.circle(quadSurface,SHAPE_BORDER_COLOR,
                        (shapeShape["pos"][0],shapeShape["pos"][1]),shapeShape["pos"][2],shapeBorderSize)
                    pygame.draw.line(quadSurface,SHAPE_BORDER_COLOR,(0,0),(0,shapeSizeOn2),shapeBorderSize)
                    pygame.draw.line(quadSurface,SHAPE_BORDER_COLOR,(0,shapeSizeOn2),(shapeSizeOn2,shapeSizeOn2),shapeBorderSize)
            elif shapeShape["type"] == "rect":
                quadSurface.fill(SHAPE_BORDER_COLOR)
                pygame.draw.rect(quadSurface,tempColor,pygame.Rect(
                    shapeBorderSize/2,
                    shapeBorderSize,
                    shapeSizeOn2-(1.5*shapeBorderSize),
                    shapeSizeOn2-(1.5*shapeBorderSize)))
            else:
                pygame.draw.polygon(quadSurface,tempColor,shapeShape["points"])
                pygame.draw.polygon(quadSurface,SHAPE_BORDER_COLOR,shapeShape["points"],shapeBorderSize)
            tempLayerSurface = pygame.Surface((shapeSize,shapeSize),flags=pygame.SRCALPHA)
            tempLayerSurface.blit(quadSurface,(tempLayerSurface.get_width()/2,0))
            tempLayerSurface = pygame.transform.rotate(tempLayerSurface,-((360/numQuads)*quadIndex))
            tempLayerSurface = pygame.transform.scale(tempLayerSurface,(
                tempLayerSurface.get_width()*(LAYER_SIZE_REDUCTION**layerIndex),
                tempLayerSurface.get_height()*(LAYER_SIZE_REDUCTION**layerIndex)))
            returnSurface.blit(tempLayerSurface,(
            (fakeSurfaceSize/2)-(tempLayerSurface.get_width()/2),
            (fakeSurfaceSize/2)-(tempLayerSurface.get_height()/2)))
    return pygame.transform.smoothscale(returnSurface,(surfaceSize,surfaceSize)) # pygame doesn't work well at low resolution so render at size 500 then downscale to the desired size
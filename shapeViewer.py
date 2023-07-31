import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os
import pygame
import globalInfos
LAYER_SIZE_REDUCTION = 0.7 # maybe it should be 0.76, maybe not
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
DEFAULT_SHAPE_DIAMETER = 407
DEFAULT_BORDER_SIZE = 15
FAKE_SURFACE_SIZE = globalInfos.INITIAL_SHAPE_SIZE
SIZE_CHANGE_RATIO = FAKE_SURFACE_SIZE / DEFAULT_IMAGE_SIZE
SHAPE_SIZE = DEFAULT_SHAPE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_BORDER_SIZE = round(DEFAULT_BORDER_SIZE*SIZE_CHANGE_RATIO)
BG_CIRCLE_DIAMETER = DEFAULT_BG_CIRCLE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_SIZE_ON_2 = SHAPE_SIZE/2
SHAPES_SHAPE = {
    "C" : {
        "type" : "circle",
        "pos" : (0,SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2)
    },
    "R" : {
        "type" : "rect",
        "pos" : (0,0,SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2)
    },
    "S" : {
        "type" : "polygon",
        "points" : [(SHAPE_SIZE_ON_2,0),(SHAPE_SIZE/4,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE/4)]
    },
    "W" : {
        "type" : "polygon",
        "points" : [(SHAPE_SIZE_ON_2,0),(SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE/4)]
    },
    "P" : {
        "type" : "circle",
        "pos" : (SHAPE_SIZE/6,SHAPE_SIZE/3,SHAPE_SIZE/12),
        "color" : (122,148,166),
        "border" : False
    },
    "c" : {
        "type" : "circle",
        "pos" : (0,SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2),
        "color" : (50,160,180),
        "border" : False
    }
}
def preRenderQuadrants() -> None:
    global preRenderedQuadrants
    for shapeKey,shape in SHAPES_SHAPE.items():
        if shape.get("color") is None:
            colors = COLORS
        else:
            colors = {"-":shape["color"]}
        for colorKey, colorValue in colors.items():
            quadSurface = pygame.Surface((SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2),flags=pygame.SRCALPHA)
            if shape["type"] == "circle":
                pygame.draw.circle(quadSurface,colorValue,
                    (shape["pos"][0],shape["pos"][1]),shape["pos"][2])
            elif shape["type"] == "rect":
                pygame.draw.rect(quadSurface,colorValue,
                    pygame.Rect(
                        shape["pos"][0],
                        shape["pos"][1],
                        shape["pos"][2],
                        shape["pos"][3]))
            else:
                pygame.draw.polygon(quadSurface,colorValue,shape["points"])
            preRenderedQuadrants[shapeKey+colorKey] = quadSurface
preRenderedQuadrants:dict[str,pygame.Surface] = {}
def renderShape(shapeCode:str,surfaceSize:int) -> pygame.Surface:
    decomposedShapeCode = shapeCode.split(":")
    numQuads = int(len(decomposedShapeCode[0])/2)
    decomposedShapeCode = [[layer[i*2:(i*2)+2] for i in range(numQuads)] for layer in decomposedShapeCode]
    returnSurface = pygame.Surface((FAKE_SURFACE_SIZE,FAKE_SURFACE_SIZE),pygame.SRCALPHA)
    pygame.draw.circle(returnSurface,BG_CIRCLE_COLOR,(FAKE_SURFACE_SIZE/2,FAKE_SURFACE_SIZE/2),BG_CIRCLE_DIAMETER/2)
    for layerIndex, layer in enumerate(decomposedShapeCode):
        curLayerSizeReduction = LAYER_SIZE_REDUCTION ** layerIndex
        for quadIndex, quad in enumerate(layer):
            if quad.startswith("-"):
                continue
            shapeShape = SHAPES_SHAPE[quad[0]]
            quadSurface = preRenderedQuadrants[quad]
            resizedQuadSurfaceSize = round(SHAPE_SIZE_ON_2*curLayerSizeReduction)
            withBorderQuadSurface = pygame.Surface(
                (resizedQuadSurfaceSize+SHAPE_BORDER_SIZE,resizedQuadSurfaceSize+SHAPE_BORDER_SIZE),
                pygame.SRCALPHA)
            quadSurface = pygame.transform.scale(quadSurface,(resizedQuadSurfaceSize,resizedQuadSurfaceSize))
            withBorderQuadSurface.blit(quadSurface,(SHAPE_BORDER_SIZE/2,SHAPE_BORDER_SIZE/2))
            if shapeShape.get("border") is not False:
                if shapeShape["type"] == "circle":
                    pygame.draw.circle(withBorderQuadSurface,SHAPE_BORDER_COLOR,
                        (
                            (shapeShape["pos"][0]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2),
                            (shapeShape["pos"][1]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2)),
                        (shapeShape["pos"][2]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2),
                        SHAPE_BORDER_SIZE,
                        draw_top_right=True)
                    pygame.draw.line(withBorderQuadSurface,SHAPE_BORDER_COLOR,
                        (SHAPE_BORDER_SIZE/2,0),
                        (SHAPE_BORDER_SIZE/2,resizedQuadSurfaceSize+SHAPE_BORDER_SIZE),
                        SHAPE_BORDER_SIZE)
                    pygame.draw.line(withBorderQuadSurface,SHAPE_BORDER_COLOR,
                        (0,resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2)),
                        (resizedQuadSurfaceSize+SHAPE_BORDER_SIZE,resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2)),
                        SHAPE_BORDER_SIZE)
                elif shapeShape["type"] == "rect":
                    pygame.draw.rect(withBorderQuadSurface,SHAPE_BORDER_COLOR,
                        pygame.Rect(
                            shapeShape["pos"][0]*curLayerSizeReduction,
                            shapeShape["pos"][1]*curLayerSizeReduction,
                            (shapeShape["pos"][2]*curLayerSizeReduction)+SHAPE_BORDER_SIZE,
                            (shapeShape["pos"][3]*curLayerSizeReduction)+SHAPE_BORDER_SIZE
                        ),
                        SHAPE_BORDER_SIZE)
                else:
                    scaledPoints = [
                        ((point[0]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2),
                         (point[1]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2)) for point in shapeShape["points"]]
                    pygame.draw.polygon(withBorderQuadSurface,SHAPE_BORDER_COLOR,scaledPoints,SHAPE_BORDER_SIZE)
                    for point in scaledPoints:
                        pygame.draw.circle(withBorderQuadSurface,SHAPE_BORDER_COLOR,point,(SHAPE_BORDER_SIZE/2)-1)
            tempLayerSurface = pygame.Surface(((resizedQuadSurfaceSize*2)+SHAPE_BORDER_SIZE,(resizedQuadSurfaceSize*2)+SHAPE_BORDER_SIZE),flags=pygame.SRCALPHA)
            tempLayerSurface.blit(withBorderQuadSurface,(resizedQuadSurfaceSize,0))
            tempLayerSurface = pygame.transform.rotate(tempLayerSurface,-((360/numQuads)*quadIndex))
            returnSurface.blit(tempLayerSurface,(
            (FAKE_SURFACE_SIZE/2)-(tempLayerSurface.get_width()/2),
            (FAKE_SURFACE_SIZE/2)-(tempLayerSurface.get_height()/2)))
    return pygame.transform.smoothscale(returnSurface,(surfaceSize,surfaceSize)) # pygame doesn't work well at low resolution so render at size 500 then downscale to the desired size
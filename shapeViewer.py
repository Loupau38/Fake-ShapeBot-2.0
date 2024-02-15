import globalInfos
import pygame

COLORS = {
    "u" : (187,187,186),
    "r" : (255,0,0),
    "g" : (0,255,0),
    "b" : (0,0,255),
    "c" : (0,255,255),
    "p" : (255,0,255),
    "y" : (255,255,0),
    "w" : (255,255,255),
    "k" : (0,0,0)
}
SHAPE_BORDER_COLOR = (42,28,42)
BG_CIRCLE_COLOR = (31,41,61,25)
SHADOW_COLOR = (50,50,50,127)

# according to 'dnSpy > ShapeMeshGenerator > GenerateShapeMesh()', this value should be 0.85
# according to ingame screenshots, it should be 0.77
# according to me, the closest is 0.8
LAYER_SIZE_REDUCTION = 0.8
DEFAULT_IMAGE_SIZE = 602
DEFAULT_BG_CIRCLE_DIAMETER = 520
DEFAULT_SHAPE_DIAMETER = 407
DEFAULT_BORDER_SIZE = 15
FAKE_SURFACE_SIZE = globalInfos.INITIAL_SHAPE_SIZE

SIZE_CHANGE_RATIO = FAKE_SURFACE_SIZE / DEFAULT_IMAGE_SIZE
SHAPE_SIZE = DEFAULT_SHAPE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_BORDER_SIZE = round(DEFAULT_BORDER_SIZE*SIZE_CHANGE_RATIO)
BG_CIRCLE_DIAMETER = DEFAULT_BG_CIRCLE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_SIZE_ON_2 = SHAPE_SIZE / 2
SHAPE_SIZE_ON_4 = SHAPE_SIZE / 4
SHAPE_SIZE_ON_8 = SHAPE_SIZE / 8
SHAPE_SIZE_ON_16 = SHAPE_SIZE / 16

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
        "points" : [(SHAPE_SIZE_ON_2,0),(SHAPE_SIZE_ON_4,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_4)]
    },
    "W" : {
        "type" : "polygon",
        "points" : [(SHAPE_SIZE_ON_2,0),(SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_4)]
    },
    "P" : {
        "type" : "circle",
        "pos" : (SHAPE_SIZE/6,SHAPE_SIZE/3,SHAPE_SIZE/12),
        "color" : (135,164,185),
        "border" : False
    },
    "c" : {
        "type" : "polygon",
        "points" : [(0,SHAPE_SIZE_ON_2),(0,SHAPE_SIZE_ON_16),
            (SHAPE_SIZE_ON_16,SHAPE_SIZE_ON_16),((SHAPE_SIZE/32)*7,0),
            (SHAPE_SIZE_ON_4,SHAPE_SIZE_ON_8),(SHAPE_SIZE_ON_8*3,SHAPE_SIZE_ON_8),
            (SHAPE_SIZE_ON_8*3,SHAPE_SIZE_ON_4),(SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_16*5),
            (SHAPE_SIZE_ON_16*7,SHAPE_SIZE_ON_16*7),(SHAPE_SIZE_ON_16*7,SHAPE_SIZE_ON_2)],
        "border" : False
    }
}

def preRenderQuadrants() -> None:

    global preRenderedQuadrants
    global preRenderedShadows

    for shapeKey,shape in SHAPES_SHAPE.items():

        if shape.get("color") is None:
            colors = COLORS
        else:
            colors = {globalInfos.SHAPE_NOTHING_CHAR:shape["color"]}

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

            if shape.get("border") is False:
                quadShadowSurface = pygame.Surface((SHAPE_SIZE_ON_2,SHAPE_SIZE_ON_2),flags=pygame.SRCALPHA)
                for x in range(quadSurface.get_width()):
                    for y in range(quadSurface.get_height()):
                        if quadSurface.get_at((x,y))[3] == 0:
                            color = (0,0,0,0)
                        else:
                            color = SHADOW_COLOR
                        quadShadowSurface.set_at((x,y),color)
                preRenderedShadows[shapeKey+colorKey] = quadShadowSurface

preRenderedQuadrants:dict[str,pygame.Surface] = {}
preRenderedShadows:dict[str,pygame.Surface] = {}

def renderShape(shapeCode:str,surfaceSize:int) -> pygame.Surface:

    decomposedShapeCode = shapeCode.split(globalInfos.SHAPE_LAYER_SEPARATOR)
    numQuads = int(len(decomposedShapeCode[0])/2)
    decomposedShapeCode = [[layer[i*2:(i*2)+2] for i in range(numQuads)] for layer in decomposedShapeCode]

    returnSurface = pygame.Surface((FAKE_SURFACE_SIZE,FAKE_SURFACE_SIZE),pygame.SRCALPHA)
    pygame.draw.circle(returnSurface,BG_CIRCLE_COLOR,(FAKE_SURFACE_SIZE/2,FAKE_SURFACE_SIZE/2),BG_CIRCLE_DIAMETER/2)

    for layerIndex, layer in enumerate(decomposedShapeCode):

        curLayerSizeReduction = LAYER_SIZE_REDUCTION ** layerIndex
        resizedQuadSurfaceSize = round(SHAPE_SIZE_ON_2*curLayerSizeReduction)
        withBorderQuadSurface = pygame.Surface(
            (resizedQuadSurfaceSize+SHAPE_BORDER_SIZE,resizedQuadSurfaceSize+SHAPE_BORDER_SIZE),
            pygame.SRCALPHA)
        tempLayerSurface = pygame.Surface((
            (resizedQuadSurfaceSize*2)+SHAPE_BORDER_SIZE,
            (resizedQuadSurfaceSize*2)+SHAPE_BORDER_SIZE),
            flags=pygame.SRCALPHA)

        for quadIndex, quad in enumerate(layer):

            if quad.startswith(globalInfos.SHAPE_NOTHING_CHAR):
                continue

            shapeShape = SHAPES_SHAPE[quad[0]]
            quadSurface = preRenderedQuadrants[quad]
            quadSurface = pygame.transform.scale(quadSurface,(resizedQuadSurfaceSize,resizedQuadSurfaceSize))
            curWithBorderQuadSurface = withBorderQuadSurface.copy()

            if (shapeShape.get("border") is False) and (layerIndex != 0):
                quadShadowSurface = preRenderedShadows[quad]
                quadShadowSurface = pygame.transform.scale(quadShadowSurface,
                    (resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2),resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2)))
                curWithBorderQuadSurface.blit(quadShadowSurface,(SHAPE_BORDER_SIZE/2,0))

            curWithBorderQuadSurface.blit(quadSurface,(SHAPE_BORDER_SIZE/2,SHAPE_BORDER_SIZE/2))

            curTempLayerSurface = tempLayerSurface.copy()
            curTempLayerSurface.blit(curWithBorderQuadSurface,(resizedQuadSurfaceSize,0))
            curTempLayerSurface = pygame.transform.rotate(curTempLayerSurface,-((360/numQuads)*quadIndex))
            returnSurface.blit(curTempLayerSurface,(
            (FAKE_SURFACE_SIZE/2)-(curTempLayerSurface.get_width()/2),
            (FAKE_SURFACE_SIZE/2)-(curTempLayerSurface.get_height()/2)))

        for quadIndex, quad in enumerate(layer):

            if quad.startswith(globalInfos.SHAPE_NOTHING_CHAR):
                continue

            shapeShape = SHAPES_SHAPE[quad[0]]

            if shapeShape.get("border") is False:
                continue

            curWithBorderQuadSurface = withBorderQuadSurface.copy()

            if shapeShape["type"] == "circle":
                pygame.draw.circle(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,
                    (
                        (shapeShape["pos"][0]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2),
                        (shapeShape["pos"][1]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2)),
                    (shapeShape["pos"][2]*curLayerSizeReduction)+(SHAPE_BORDER_SIZE/2),
                    SHAPE_BORDER_SIZE,
                    draw_top_right=True)
                pygame.draw.line(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,
                    (SHAPE_BORDER_SIZE/2,0),
                    (SHAPE_BORDER_SIZE/2,resizedQuadSurfaceSize+SHAPE_BORDER_SIZE),
                    SHAPE_BORDER_SIZE)
                pygame.draw.line(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,
                    (0,resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2)),
                    (resizedQuadSurfaceSize+SHAPE_BORDER_SIZE,resizedQuadSurfaceSize+(SHAPE_BORDER_SIZE/2)),
                    SHAPE_BORDER_SIZE)

            elif shapeShape["type"] == "rect":
                pygame.draw.rect(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,
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
                pygame.draw.polygon(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,scaledPoints,SHAPE_BORDER_SIZE)
                for point in scaledPoints:
                    pygame.draw.circle(curWithBorderQuadSurface,SHAPE_BORDER_COLOR,point,(SHAPE_BORDER_SIZE/2)-1)

            curTempLayerSurface = tempLayerSurface.copy()
            curTempLayerSurface.blit(curWithBorderQuadSurface,(resizedQuadSurfaceSize,0))
            curTempLayerSurface = pygame.transform.rotate(curTempLayerSurface,-((360/numQuads)*quadIndex))
            returnSurface.blit(curTempLayerSurface,(
            (FAKE_SURFACE_SIZE/2)-(curTempLayerSurface.get_width()/2),
            (FAKE_SURFACE_SIZE/2)-(curTempLayerSurface.get_height()/2)))

    return pygame.transform.smoothscale(returnSurface,(surfaceSize,surfaceSize)) # pygame doesn't work well at low resolution so render at size 500 then downscale to the desired size
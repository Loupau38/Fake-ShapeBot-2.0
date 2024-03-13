import globalInfos
import pygame
import math

COLORS:dict[str,tuple[int,int,int]] = {
    "u" : (187,187,186),
    "r" : (255,0,0),
    "g" : (0,255,0),
    "b" : (0,0,255),
    "c" : (0,255,255),
    "p" : (255,0,255),
    "y" : (255,255,0),
    "w" : (255,255,255),
    "k" : (35,35,35)
}
SHAPE_BORDER_COLOR = (35,25,35)
BG_CIRCLE_COLOR = (31,41,61,25)
SHADOW_COLOR = (50,50,50,127)
EMPTY_COLOR = (0,0,0,0)
PIN_COLOR = (135,164,185)

# according to 'dnSpy > ShapeMeshGenerator > GenerateShapeMesh()', this value should be 0.85
# according to ingame screenshots, it should be 0.77
# according to me, the closest to ingame is 0.8
# but, to me, the best for this context is 0.75
LAYER_SIZE_REDUCTION = 0.75

# below are sizes in pixels taken from a screenshot of the ingame shape viewer
DEFAULT_IMAGE_SIZE = 602
DEFAULT_BG_CIRCLE_DIAMETER = 520
DEFAULT_SHAPE_DIAMETER = 407
DEFAULT_BORDER_SIZE = 15

FAKE_SURFACE_SIZE = globalInfos.INITIAL_SHAPE_SIZE
SIZE_CHANGE_RATIO = FAKE_SURFACE_SIZE / DEFAULT_IMAGE_SIZE
SHAPE_SIZE = DEFAULT_SHAPE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_BORDER_SIZE = round(DEFAULT_BORDER_SIZE*SIZE_CHANGE_RATIO)
BG_CIRCLE_DIAMETER = DEFAULT_BG_CIRCLE_DIAMETER * SIZE_CHANGE_RATIO

def _getScaledShapeSize(shapeSize:float,layerIndex:int) -> float:
    return shapeSize * (LAYER_SIZE_REDUCTION**layerIndex)

def _drawQuadrant(quadShape:str,quadColor:str,shapeSize:float,quadIndex:int,layerIndex:int,
    layers:list[list[str]]) -> tuple[pygame.Surface|None,pygame.Surface|None]:
    # returns quadrant with shadow, border

    borderSize = SHAPE_BORDER_SIZE
    halfBorderSize = borderSize / 2
    curShapeSize = _getScaledShapeSize(shapeSize,layerIndex)
    curQuadSize = curShapeSize / 2

    withBorderQuadSize = round(curQuadSize+borderSize)
    quadSurface = pygame.Surface(
        (withBorderQuadSize,)*2,
        pygame.SRCALPHA
    )
    quadSurfaceForBorder = quadSurface.copy()

    drawShadow = layerIndex != 0
    color = COLORS.get(quadColor)
    borderColor = SHAPE_BORDER_COLOR

    if quadShape == globalInfos.SHAPE_NOTHING_CHAR:
        return None, None

    if quadShape == "C":

        pygame.draw.circle(quadSurface,color, # main circle
            (halfBorderSize,withBorderQuadSize-halfBorderSize),
            curQuadSize,
            draw_top_right=True
        )

        pygame.draw.circle(quadSurfaceForBorder,borderColor, # circle border
            (halfBorderSize,withBorderQuadSize-halfBorderSize),
            curQuadSize+halfBorderSize,
            borderSize,
            draw_top_right=True
        )
        pygame.draw.line(quadSurfaceForBorder,borderColor, # left border
            (halfBorderSize,0),
            (halfBorderSize,withBorderQuadSize),
            borderSize
        )
        pygame.draw.line(quadSurfaceForBorder,borderColor, # down border
            (0,withBorderQuadSize-halfBorderSize),
            (withBorderQuadSize,withBorderQuadSize-halfBorderSize),
            borderSize
        )

        return quadSurface, quadSurfaceForBorder

    if quadShape == "R":

        pygame.draw.rect(quadSurface,color, # main rect
            pygame.Rect(halfBorderSize,halfBorderSize,curQuadSize,curQuadSize)
        )

        pygame.draw.rect(quadSurfaceForBorder,borderColor, # rect border
            pygame.Rect(0,0,withBorderQuadSize,withBorderQuadSize),
            borderSize
        )

        return quadSurface, quadSurfaceForBorder

    if quadShape == "S":

        points = [(curQuadSize,0),(curQuadSize/2,curQuadSize),(0,curQuadSize),(0,curQuadSize/2)]
        points = [(halfBorderSize+x,halfBorderSize+y) for x,y in points]

        pygame.draw.polygon(quadSurface,color,points) # main polygon

        pygame.draw.polygon(quadSurfaceForBorder,borderColor,points,borderSize) # border polygon
        for point in points:
            pygame.draw.circle(quadSurfaceForBorder,borderColor,point,halfBorderSize-1) # fill in the missing vertices

        return quadSurface, quadSurfaceForBorder

    if quadShape == "W":

        arcCenter = (halfBorderSize+(curQuadSize*1.4),halfBorderSize+(curQuadSize*-0.4))
        arcRadius = curQuadSize * 1.18
        sideLength = curQuadSize / 3.75

        pygame.draw.rect(quadSurface,color, # first fill in the whole quadrant
            pygame.Rect(halfBorderSize,halfBorderSize,curQuadSize,curQuadSize)
        )
        pygame.draw.circle(quadSurface,EMPTY_COLOR,arcCenter,arcRadius) # then carve out a circle

        pygame.draw.circle(quadSurfaceForBorder,borderColor,arcCenter,arcRadius+halfBorderSize,borderSize) # arc border
        pygame.draw.line(quadSurfaceForBorder,borderColor, # left border
            (halfBorderSize,0),
            (halfBorderSize,withBorderQuadSize),
            borderSize
        )
        pygame.draw.line(quadSurfaceForBorder,borderColor, # down border
            (0,withBorderQuadSize-halfBorderSize),
            (withBorderQuadSize,withBorderQuadSize-halfBorderSize),
            borderSize
        )
        pygame.draw.line(quadSurfaceForBorder,borderColor, # top edge border
            (halfBorderSize,halfBorderSize),
            (halfBorderSize+sideLength,halfBorderSize),
            borderSize
        )
        pygame.draw.line(quadSurfaceForBorder,borderColor, # right edge border
            (withBorderQuadSize-halfBorderSize,withBorderQuadSize-halfBorderSize-sideLength),
            (withBorderQuadSize-halfBorderSize,withBorderQuadSize-halfBorderSize),
            borderSize
        )

        return quadSurface, quadSurfaceForBorder

    if quadShape == "P":

        pinCenter = (halfBorderSize+(curQuadSize/3),halfBorderSize+(2*(curQuadSize/3)))
        pinRadius = curQuadSize/6

        if drawShadow:
            pygame.draw.circle(quadSurface,SHADOW_COLOR,pinCenter,pinRadius+halfBorderSize) # shadow

        pygame.draw.circle(quadSurface,PIN_COLOR,pinCenter,pinRadius) # main circle

        return quadSurface, None

    if quadShape == "c":

        darkenedColor = tuple(round(c/2) for c in color)
        darkenedAreasOffset = 0 if layerIndex%2 == 0 else 22.5
        startAngle1 = math.radians(67.5-darkenedAreasOffset)
        stopAngle1 = math.radians(90-darkenedAreasOffset)
        startAngle2 = math.radians(22.5-darkenedAreasOffset)
        stopAngle2 = math.radians(45-darkenedAreasOffset)
        darkenedAreasRect = pygame.Rect(
            halfBorderSize - curQuadSize,
            halfBorderSize,
            2 * curQuadSize,
            2 * curQuadSize
        )

        if drawShadow:
            pygame.draw.circle(quadSurface,SHADOW_COLOR, # shadow
                (halfBorderSize,withBorderQuadSize-halfBorderSize),
                curQuadSize+halfBorderSize,
                borderSize,
                draw_top_right=True
            )

        pygame.draw.circle(quadSurface,color, # main circle
            (halfBorderSize,withBorderQuadSize-halfBorderSize),
            curQuadSize,
            draw_top_right=True
        )
        pygame.draw.arc(quadSurface,darkenedColor, # 1st darkened area
            darkenedAreasRect,
            startAngle1,
            stopAngle1,
            math.ceil(curQuadSize)
        )
        pygame.draw.arc(quadSurface,darkenedColor, # 2nd darkened area
            darkenedAreasRect,
            startAngle2,
            stopAngle2,
            math.ceil(curQuadSize)
        )

        return quadSurface, None

    raise ValueError(f"Unknown shape type : {quadShape}")

def _rotateAndBlitSurf(toRotate:pygame.Surface,blitTo:pygame.Surface,numQuads:int,quadIndex:int,layerIndex:int,shapeSize:float) -> None:
    curShapeSize = _getScaledShapeSize(shapeSize,layerIndex)
    tempSurf = pygame.Surface(
        (curShapeSize+SHAPE_BORDER_SIZE,)*2,
        pygame.SRCALPHA
    )
    tempSurf.blit(toRotate,(curShapeSize/2,0))
    tempSurf = pygame.transform.rotate(tempSurf,-((360/numQuads)*quadIndex))
    blitTo.blit(tempSurf,(
        (blitTo.get_width()/2)-(tempSurf.get_width()/2),
        (blitTo.get_height()/2)-(tempSurf.get_height()/2)
    ))

def renderShape(shapeCode:str,surfaceSize:int) -> pygame.Surface:

    decomposedShapeCode = shapeCode.split(globalInfos.SHAPE_LAYER_SEPARATOR)
    numQuads = int(len(decomposedShapeCode[0])/2)
    decomposedShapeCode = [[layer[i*2:(i*2)+2] for i in range(numQuads)] for layer in decomposedShapeCode]

    returnSurface = pygame.Surface((FAKE_SURFACE_SIZE,FAKE_SURFACE_SIZE),pygame.SRCALPHA)
    pygame.draw.circle(returnSurface,BG_CIRCLE_COLOR,(FAKE_SURFACE_SIZE/2,FAKE_SURFACE_SIZE/2),BG_CIRCLE_DIAMETER/2)

    for layerIndex, layer in enumerate(decomposedShapeCode):

        quadBorders = []

        for quadIndex, quad in enumerate(layer):

            quadSurface, quadBorder = _drawQuadrant(quad[0],quad[1],SHAPE_SIZE,quadIndex,layerIndex,decomposedShapeCode)
            quadBorders.append(quadBorder)

            if quadSurface is None:
                continue

            _rotateAndBlitSurf(quadSurface,returnSurface,numQuads,quadIndex,layerIndex,SHAPE_SIZE)

        for quadIndex, border in enumerate(quadBorders):

            if border is None:
                continue

            _rotateAndBlitSurf(border,returnSurface,numQuads,quadIndex,layerIndex,SHAPE_SIZE)

    return pygame.transform.smoothscale(returnSurface,(surfaceSize,surfaceSize)) # pygame doesn't work well at low resolution so render at size 500 then downscale to the desired size
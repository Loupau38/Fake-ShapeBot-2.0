import globalInfos
import math

NOTHING_CHAR = globalInfos.SHAPE_NOTHING_CHAR
PIN_CHAR = "P"
CRYSTAL_CHAR = "c"
UNCOLORABLE_SHAPES = [CRYSTAL_CHAR,PIN_CHAR,NOTHING_CHAR]
REPLACED_BY_CRYSTAL = [PIN_CHAR,NOTHING_CHAR]

class Quadrant:

    def __init__(self,shape:str,color:str) -> None:
        self.shape = shape
        self.color = color

class Shape:

    def __init__(self,layers:list[list[Quadrant]]) -> None:
        self.layers = layers
        self.numLayers = len(layers)
        self.numQuads = len(layers[0])

    def fromListOfLayers(layers:list[str]):
        newLayers:list[list[Quadrant]] = []
        numQuads = int(len(layers[0])/2)
        for layer in layers:
            newLayers.append([])
            for quadIndex in range(numQuads):
                newLayers[-1].append(Quadrant(layer[quadIndex*2],layer[(quadIndex*2)+1]))
        return Shape(newLayers)

    def fromShapeCode(shapeCode:str):
        return Shape.fromListOfLayers(shapeCode.split(globalInfos.SHAPE_LAYER_SEPARATOR))

    def toListOfLayers(self) -> list[str]:
        return ["".join(q.shape+q.color for q in l) for l in self.layers]

    def toShapeCode(self) -> str:
        return globalInfos.SHAPE_LAYER_SEPARATOR.join(self.toListOfLayers())

def cut(shape:Shape) -> tuple[Shape,Shape]:
    takeQuads = math.ceil(shape.numQuads/2)
    shapeA = []
    shapeB = []
    for layer in shape.layers:
        shapeA.append([*([Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*(shape.numQuads-takeQuads)),*(layer[:takeQuads])])
        shapeB.append([*(layer[takeQuads:]),*([Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*(takeQuads))])
    return Shape(shapeA), Shape(shapeB)

def halfCut(shape:Shape) -> Shape:
    return cut(shape)[1]

def rotate90CW(shape:Shape) -> Shape:
    newLayers = []
    for layer in shape.layers:
        newLayers.append([layer[-1],*(layer[:-1])])
    return Shape(newLayers)

def rotate90CCW(shape:Shape) -> Shape:
    newLayers = []
    for layer in shape.layers:
        newLayers.append([*(layer[1:]),layer[0]])
    return Shape(newLayers)

def rotate180(shape:Shape) -> Shape:
    takeQuads = math.ceil(shape.numQuads/2)
    newLayers = []
    for layer in shape.layers:
        newLayers.append([*(layer[takeQuads:]),*(layer[:takeQuads])])
    return Shape(newLayers)

def swapHalves(shapeA:Shape,shapeB:Shape) -> tuple[Shape,Shape]:
    pass

def stack(bottomShape:Shape,topShape:Shape) -> Shape:
    pass

def topPaint(shape:Shape,color:str) -> Shape:
    newLayers = shape.layers[:-1]
    newLayers.append([Quadrant(q.shape,NOTHING_CHAR if q.shape in UNCOLORABLE_SHAPES else color) for q in shape.layers[-1]])
    return Shape(newLayers)

def fullPaint(shape:Shape,color:str) -> Shape:
    return Shape([[Quadrant(q.shape,NOTHING_CHAR if q.shape in UNCOLORABLE_SHAPES else color) for q in l] for l in shape.layers])

def pushPin(shape:Shape) -> Shape:
    return Shape([[Quadrant("P",NOTHING_CHAR),*(l[1:])] for l in shape.layers])

def genCrystal(shape:Shape,color:str) -> Shape:
    return Shape([[Quadrant(CRYSTAL_CHAR,color) if q.shape in REPLACED_BY_CRYSTAL else q for q in l] for l in shape.layers])
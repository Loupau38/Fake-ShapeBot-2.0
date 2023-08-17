import globalInfos
import math

NOTHING_CHAR = globalInfos.SHAPE_NOTHING_CHAR
PIN_CHAR = "P"
CRYSTAL_CHAR = "c"
UNPAINTABLE_SHAPES = [CRYSTAL_CHAR,PIN_CHAR,NOTHING_CHAR]
REPLACED_BY_CRYSTAL = [PIN_CHAR,NOTHING_CHAR]
MAX_STACKER_LAYERS = 4

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
    
    def isEmpty(self) -> bool:
        return all(c == NOTHING_CHAR for c in "".join(self.toListOfLayers()))

class InvalidOperationInputs(ValueError): ...

def getCorrectedIndex(list:list,index:int) -> int:
    if index > len(list)-1:
        return index - len(list)
    if index < 0:
        return len(list) + index
    return index

def getConnected(layer:list[Quadrant],index:int,matchShape:bool=False) -> list[int]:
    def checkQuad(curQuad:Quadrant) -> bool:
        return ((curQuad.shape != quad.shape) if matchShape else (curQuad.shape in (NOTHING_CHAR,PIN_CHAR)))
    connected = [index]
    quad = layer[index]
    if quad.shape == NOTHING_CHAR:
        return []
    if quad.shape == PIN_CHAR:
        return [index]
    for i in range(index+1,len(layer)+index):
        curIndex = getCorrectedIndex(layer,i)
        curQuad:Quadrant = layer[curIndex]
        if checkQuad(curQuad):
            break
        connected.append(curIndex)
    for i in range(index-1,-len(layer)+index,-1):
        curIndex = getCorrectedIndex(layer,i)
        if curIndex in connected:
            break
        curQuad:Quadrant = layer[curIndex]
        if checkQuad(curQuad):
            break
        connected.append(curIndex)
    return connected

def makeLayersFall(layers:list[list[Quadrant]]) -> list[list[Quadrant]]:
    def sepInGroups(layer:list[Quadrant]) -> list[list[int]]:
        handledIndexes = []
        groups = []
        for quadIndex,_ in enumerate(layer):
            if quadIndex in handledIndexes:
                continue
            group = getConnected(layer,quadIndex)
            if group != []:
                groups.append(group)
                handledIndexes.extend(group)
        return groups
    for layerIndex,layer in enumerate(layers):
        if layerIndex == 0:
            continue
        for group in sepInGroups(layer):
            fall = True
            for quadIndex in group:
                if layers[layerIndex-1][quadIndex].shape != NOTHING_CHAR:
                    fall = False
                    break
            if fall:
                for quadIndex in group:
                    if layer[quadIndex].shape == CRYSTAL_CHAR:
                        layer[quadIndex] = Quadrant(NOTHING_CHAR,NOTHING_CHAR)
        for group in sepInGroups(layer):
            for layerIndex2 in range(layerIndex,0,-1):
                fall = True
                for quadIndex in group:
                    if layers[layerIndex2-1][quadIndex].shape != NOTHING_CHAR:
                        fall = False
                        break
                if not fall:
                    break
                for quadIndex in group:
                    layers[layerIndex2-1][quadIndex] = layers[layerIndex2][quadIndex]
                    layers[layerIndex2][quadIndex] = Quadrant(NOTHING_CHAR,NOTHING_CHAR)
    return layers

def cleanUpEmptyUpperLayers(layers:list[list[Quadrant]]) -> list[list[Quadrant]]:
    if len(layers) == 1:
        return layers
    for i in range(len(layers)-1,-1,-1):
        if any((q.shape != NOTHING_CHAR) for q in layers[i]):
            break
    return layers[:i+1]

def crystalsUnsupported(shape:Shape|list[Shape],op:str) -> None:
    if type(shape) == list:
        layers = []
        for s in shape:
            layers.extend(s.layers)
    else:
        layers = shape.layers
    for l in layers:
        for q in l:
            if q.shape == CRYSTAL_CHAR:
                raise InvalidOperationInputs(f"Crystals not supported for operation '{op}'")

def differentNumQuadsUnsupported(func):
    def wrapper(*args,**kwargs) -> None:
        shapes:list[Shape] = []
        for arg in args:
            if type(arg) == Shape:
                shapes.append(arg)
        if shapes != []:
            expected = shapes[0].numQuads
            for shape in shapes[1:]:
                if shape.numQuads != expected:
                    raise InvalidOperationInputs(
                        f"Shapes with differing number of quadrants per layer are not supported for operation '{func.__name__}'")
        return func(*args,**kwargs)
    return wrapper

def cut(shape:Shape) -> list[Shape]:
    takeQuads = math.ceil(shape.numQuads/2)
    cutPoints = [(0,shape.numQuads-1),(shape.numQuads-takeQuads,shape.numQuads-takeQuads-1)]
    for layer in shape.layers:
        for cutPoint in cutPoints:
            if (layer[cutPoint[0]].shape == CRYSTAL_CHAR) and (layer[cutPoint[1]].shape == CRYSTAL_CHAR):
                toBreak = [*getConnected(layer,cutPoint[0],True),*getConnected(layer,cutPoint[1],True)]
                for quadIndex in toBreak:
                    layer[quadIndex] = Quadrant(NOTHING_CHAR,NOTHING_CHAR)
    shapeA = []
    shapeB = []
    for layer in shape.layers:
        shapeA.append([*([Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*(shape.numQuads-takeQuads)),*(layer[-takeQuads:])])
        shapeB.append([*(layer[:-takeQuads]),*([Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*(takeQuads))])
    shapeA, shapeB = [cleanUpEmptyUpperLayers(makeLayersFall(s)) for s in (shapeA,shapeB)]
    return [Shape(shapeA),Shape(shapeB)]

def halfCut(shape:Shape) -> list[Shape]:
    return [cut(shape)[1]]

def rotate90CW(shape:Shape) -> list[Shape]:
    newLayers = []
    for layer in shape.layers:
        newLayers.append([layer[-1],*(layer[:-1])])
    return [Shape(newLayers)]

def rotate90CCW(shape:Shape) -> list[Shape]:
    newLayers = []
    for layer in shape.layers:
        newLayers.append([*(layer[1:]),layer[0]])
    return [Shape(newLayers)]

def rotate180(shape:Shape) -> list[Shape]:
    takeQuads = math.ceil(shape.numQuads/2)
    newLayers = []
    for layer in shape.layers:
        newLayers.append([*(layer[takeQuads:]),*(layer[:takeQuads])])
    return [Shape(newLayers)]

@differentNumQuadsUnsupported
def swapHalves(shapeA:Shape,shapeB:Shape) -> list[Shape]:
    numLayers = max(shapeA.numLayers,shapeB.numLayers)
    takeQuads = math.ceil(shapeA.numQuads/2)
    shapeACut, shapeBCut = cut(shapeA), cut(shapeB)
    shapeACut = [[*s.layers,*([[Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*shapeA.numQuads]*(numLayers-len(s.layers)))] for s in shapeACut]
    shapeBCut = [[*s.layers,*([[Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*shapeB.numQuads]*(numLayers-len(s.layers)))] for s in shapeBCut]
    returnShapeA = []
    returnShapeB = []
    for layerA0,layerA1,layerB0,layerB1 in zip(*shapeACut,*shapeBCut):
        returnShapeA.append([*(layerB1[:-takeQuads]),*(layerA0[-takeQuads:])])
        returnShapeB.append([*(layerA1[:-takeQuads]),*(layerB0[-takeQuads:])])
    returnShapeA, returnShapeB = cleanUpEmptyUpperLayers(returnShapeA),cleanUpEmptyUpperLayers(returnShapeB)
    return [Shape(returnShapeA),Shape(returnShapeB)]

@differentNumQuadsUnsupported
def stack(bottomShape:Shape,topShape:Shape) -> list[Shape]:
    newTopShape = [[Quadrant(NOTHING_CHAR,NOTHING_CHAR) if q.shape == CRYSTAL_CHAR else q for q in l] for l in topShape.layers]
    newLayers = [*bottomShape.layers,*newTopShape]
    newLayers = cleanUpEmptyUpperLayers(makeLayersFall(newLayers))
    newLayers = newLayers[:MAX_STACKER_LAYERS]
    return [Shape(newLayers)]

def topPaint(shape:Shape,color:str) -> list[Shape]:
    newLayers = shape.layers[:-1]
    newLayers.append([Quadrant(q.shape,NOTHING_CHAR if q.shape in UNPAINTABLE_SHAPES else color) for q in shape.layers[-1]])
    return [Shape(newLayers)]

def fullPaint(shape:Shape,color:str) -> list[Shape]:
    return [Shape([[Quadrant(q.shape,NOTHING_CHAR if q.shape in UNPAINTABLE_SHAPES else color) for q in l] for l in shape.layers])]

def pushPin(shape:Shape) -> list[Shape]:
    newLayers = []
    for i,layer in enumerate(shape.layers):
        newLayer = layer
        if newLayer[0].shape == CRYSTAL_CHAR:
            for quadIndex in getConnected(newLayer,0,True):
                newLayer[quadIndex] = Quadrant(NOTHING_CHAR,NOTHING_CHAR)
        if i == 0:
            newLayer[0] = Quadrant(PIN_CHAR,NOTHING_CHAR)
        newLayers.append(newLayer)
    newLayers = cleanUpEmptyUpperLayers(newLayers)
    return [Shape(newLayers)]

def genCrystal(shape:Shape,color:str) -> list[Shape]:
    return [Shape([[Quadrant(CRYSTAL_CHAR,color) if q.shape in REPLACED_BY_CRYSTAL else q for q in l] for l in shape.layers])]

def unstack(shape:Shape) -> list[Shape]:
    if shape.numLayers == 1:
        return Shape([[Quadrant(NOTHING_CHAR,NOTHING_CHAR)]*shape.numQuads]),shape.layers[0]
    return [Shape(shape.layers[:-1]),Shape([shape.layers[-1]])]
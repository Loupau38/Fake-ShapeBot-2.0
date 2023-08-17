import shapeOperations
import shapeCodeGenerator
import globalInfos
import shapeViewer
import pygame
import io

class Operation:

    def __init__(self,numInputs:int,numOutputs:int,fullName:str,func,colorInputIndexes:list[int]|None=None) -> None:
        self.numInputs = numInputs
        self.numOutputs = numOutputs
        self.fullName = fullName
        self.func = func
        self.colorInputindexes = [] if colorInputIndexes is None else colorInputIndexes
        self.image = None

class Instruction:

    DEF = "def"
    OP = "op"

    def __init__(self,type:str,*,shapeVars:list[int]|None=None,shapeCodes:list[str]|None=None,
            inputShapeVars:list[int]|None=None,inputColorVars:list[str]|None=None,operation:Operation|None=None,outputShapeVars:list[int]|None=None) -> None:
        self.type = type
        if type == Instruction.DEF:
            self.vars = shapeVars
            self.shapeCodes = shapeCodes
        else:
            self.inputs = inputShapeVars
            self.colorInputs = inputColorVars
            self.op = operation
            self.outputs = outputShapeVars

class GraphNode:

    SHAPE = "shape"
    OP = "op"

    def __init__(self,type:str,inputs:list[int]|None,outputs:list[int]|None,image:pygame.Surface,
        shapeVar:int|None=None,shapeCode:str|None=None) -> None:
        self.type = type
        self.inputs = inputs
        self.outputs = outputs
        self.image = image
        self.shapeVar = shapeVar
        self.shapeCode = shapeCode
        self.layer = None
        self.pos = None

INSTRUCTION_SEPARATOR = ";"
DEFINITION_SEPARATOR = "="
VALUE_SEPARATOR = ","
OPERATION_SEPARATOR = ":"

IMAGES_START_PATH = "./operationGraphImages/"

GRAPH_NODE_SIZE = 100
GRAPH_H_MARGIN = 100
GRAPH_V_MARGIN = 200
LINE_COLOR = (127,127,127)
LINE_WIDTH = 5

OPERATIONS:dict[str,Operation] = {
    "cut" : Operation(1,2,"Cut",shapeOperations.cut),
    "hcut" : Operation(1,1,"Half cut",shapeOperations.halfCut),
    "r90cw" : Operation(1,1,"Rotate 90° clockwise",shapeOperations.rotate90CW),
    "r90ccw" : Operation(1,1,"Rotate 90° counterclockwise",shapeOperations.rotate90CCW),
    "r180" : Operation(1,1,"Rotate 180°",shapeOperations.rotate180),
    "sh" : Operation(2,2,"Swap halves",shapeOperations.swapHalves),
    "stack" : Operation(2,1,"Stack",shapeOperations.stack),
    "paint" : Operation(2,1,"Paint",shapeOperations.topPaint,[1]),
    "pin" : Operation(1,1,"Push pin",shapeOperations.pushPin),
    "crystal" : Operation(2,1,"Generate crystals",shapeOperations.genCrystal,[1]),
    "unstack" : Operation(1,2,"Unstack",shapeOperations.unstack)
}

for k,v in OPERATIONS.items():
    try:
        v.image = pygame.image.load(f"{IMAGES_START_PATH}{k}.png")
    except FileNotFoundError:
        pass

pygame.font.init()
SHAPE_VAR_FONT = pygame.font.SysFont("arial",30)
SHAPE_VAR_COLOR = (255,255,255)

def getInstructionsFromText(text:str) -> tuple[bool,list[Instruction]|str]:

    def decodeInstruction(instruction:str) -> tuple[bool,str|Instruction]:

        if DEFINITION_SEPARATOR in instruction:

            if instruction.count(DEFINITION_SEPARATOR) > 1:
                return False,f"Max 1 '{DEFINITION_SEPARATOR}' per instruction"

            shapeVars, shapeCode = instruction.split(DEFINITION_SEPARATOR)
            if shapeVars == "":
                return False,"Empty variables section"
            if shapeCode == "":
                return False,"Empty shape code section"

            shapeVars = shapeVars.split(VALUE_SEPARATOR)
            shapeVarsInt = []
            for i,sv in enumerate(shapeVars):
                try:
                    shapeVarsInt.append(int(sv))
                except ValueError:
                    return False, f"Shape variable {i+1} not an integer"

            shapeCodesOrError, isShapeCodeValid = shapeCodeGenerator.generateShapeCodes(shapeCode)
            if not isShapeCodeValid:
                return False,f"Error decoding shape code : {shapeCodesOrError}"

            if len(shapeCodesOrError) != len(shapeVarsInt):
                return False, f"Number of shape codes outputed isn't the same as number of shape variables given \
                    ({len(shapeCodesOrError)} vs {len(shapeVarsInt)})"

            return True,Instruction(Instruction.DEF,shapeVars=shapeVarsInt,shapeCodes=shapeCodesOrError)

        if instruction.count(OPERATION_SEPARATOR) != 2:
            return False,f"Operation instruction must contain 2 '{OPERATION_SEPARATOR}'"

        inputs, op, outputs = instruction.split(OPERATION_SEPARATOR)
        for k,v in {"inputs":inputs,"operation":op,"outputs":outputs}.items():
            if v == "":
                return False,f"Empty {k} section"

        if OPERATIONS.get(op) is None:
            return False,f"Unknown operation '{op}'"

        inputs = [i.replace("m","p") for i in inputs.split(VALUE_SEPARATOR)]
        outputs = outputs.split(VALUE_SEPARATOR)
        inputsInt = []
        colorInputs = []
        outputsInt = []
        curOperation = OPERATIONS.get(op)

        for i,input in enumerate(inputs):
            if i in curOperation.colorInputindexes:
                if input not in globalInfos.SHAPE_COLORS:
                    return False,f"Input {i+1} must be a color"
                colorInputs.append(input)
            else:
                try:
                    inputsInt.append(int(input))
                except ValueError:
                    return False,f"Input {i+1} not an integer"

        for i,output in enumerate(outputs):
            try:
                outputsInt.append(int(output))
            except ValueError:
                return False,f"Output {i+1} not an integer"

        for e,g,t in zip((curOperation.numInputs,curOperation.numOutputs),(len(inputsInt)+len(colorInputs),len(outputsInt)),("inputs","outputs")):
            if e != g:
                print(outputsInt)
                return False,f"Number of operation {t} isn't the same as number of {t} given ({e} vs {g})"

        return True,Instruction(Instruction.OP,inputShapeVars=inputsInt,inputColorVars=colorInputs,
            operation=curOperation,outputShapeVars=outputsInt)

    if text == "":
        return False,"Empty text"

    instructions = text.split(INSTRUCTION_SEPARATOR)
    decodedInstructions = []

    for i,instruction in enumerate(instructions):
        valid, decodedInstructionOrError = decodeInstruction(instruction)
        if not valid:
            return False,f"Error in instruction {i+1} : {decodedInstructionOrError}"
        decodedInstructions.append(decodedInstructionOrError)

    return True,decodedInstructions

def genOperationGraph(instructions:list[Instruction],showShapeVars:bool) -> tuple[bool,str|tuple[io.BytesIO,dict[int,str]]]:

    seenInputVars = []
    seenOutputVars = []

    for i,instruction in enumerate(instructions):

        errMsgStart = f"Error in instruction {i+1} : "

        if instruction.type == Instruction.DEF:

            for var in instruction.vars:
                if var in seenOutputVars:
                    return False,f"{errMsgStart}Variable '{var}' cannot be used as output/defined to multiple times"
                seenOutputVars.append(var)

        else:

            for var in instruction.inputs:
                if var in instruction.outputs:
                    return False,f"{errMsgStart}Variable '{var}' cannot be used as input and output in the same instruction"
                if var in seenInputVars:
                    return False,f"{errMsgStart}Variable '{var}' cannot be used as input multiple times"
                seenInputVars.append(var)

            for var in instruction.outputs:
                if var in seenOutputVars:
                    return False,f"{errMsgStart}Variable '{var}' cannot be used as output/defined to multiple times"
                seenOutputVars.append(var)

    for siv in seenInputVars:
        if siv not in seenOutputVars:
            return False,f"Variable '{siv}' is not used as output"

    newInstructions = []
    for instruction in instructions:
        if instruction.type == Instruction.OP:
            newInstructions.append(instruction)
            continue
        for var,code in zip(instruction.vars,instruction.shapeCodes):
            newInstructions.append(Instruction(Instruction.DEF,shapeVars=[var],shapeCodes=[code]))

    instructions = newInstructions.copy()

    inputLocations = {}
    outputLocations = {}

    for i,instruction in enumerate(instructions):
        if instruction.type == Instruction.DEF:
            outputLocations[instruction.vars[0]] = i
        else:
            for input in instruction.inputs:
                inputLocations[input] = i
            for output in instruction.outputs:
                outputLocations[output] = i

    graphNodes:dict[int,GraphNode] = {}
    curId = 0
    handledInstructions = {}

    def renderShape(shapeCode) -> pygame.Surface:
        return shapeViewer.renderShape(shapeCode,GRAPH_NODE_SIZE)

    def newId() -> int:
        nonlocal curId
        curId += 1
        return curId - 1

    def genGraphNode(instruction:Instruction,instructionIndex:int) -> int:

        def createFinalOutputShape(inputs:list[int],shapeCode:str,shapeVar:int) -> int:
            curId = newId()
            graphNodes[curId] = GraphNode(GraphNode.SHAPE,inputs,None,renderShape(shapeCode),shapeVar,shapeCode)
            return curId

        if instructionIndex in handledInstructions:
            return handledInstructions[instructionIndex]

        if instruction.type == Instruction.DEF:

            curShapeVar = instruction.vars[0]
            curShapeCode = instruction.shapeCodes[0]

            curId = newId()
            graphNodes[curId] = GraphNode(GraphNode.SHAPE,None,None,
                renderShape(curShapeCode),curShapeVar,curShapeCode)
            handledInstructions[instructionIndex] = curId

            connectedInstructionLocation = inputLocations.get(curShapeVar)
            if connectedInstructionLocation is None:
                connectedNodeId = createFinalOutputShape([],curShapeCode,curShapeVar)
            else:
                connectedNodeId = genGraphNode(instructions[connectedInstructionLocation],connectedInstructionLocation)

            graphNodes[connectedNodeId].inputs.append(curId)
            graphNodes[curId].outputs = [connectedNodeId]
            return curId

        connectedInputs = []
        inputShapeCodes = []

        curCurId = newId()
        graphNodes[curCurId] = GraphNode(GraphNode.OP,[],[],instruction.op.image)
        handledInstructions[instructionIndex] = curCurId

        for input in instruction.inputs:
            inputLocation = outputLocations[input]
            inputNodeId = genGraphNode(instructions[inputLocation],inputLocation)
            if graphNodes[inputNodeId].type == GraphNode.SHAPE:
                connectedInput = inputNodeId
            else:
                for output in graphNodes[inputNodeId].outputs:
                    if graphNodes[output].shapeVar == input:
                        connectedInput = output
                        break

            connectedInputs.append(connectedInput)
            inputShapeCodes.append(graphNodes[connectedInput].shapeCode)

        graphNodes[curCurId].inputs.extend(connectedInputs)

        outputShapeCodes = instruction.op.func(*[shapeOperations.Shape.fromShapeCode(s) for s in inputShapeCodes],*instruction.colorInputs)
        outputShapeCodes = [s.toShapeCode() for s in outputShapeCodes]

        toGenOutputs = []

        for output,outputShapeCode in zip(instruction.outputs,outputShapeCodes):
            outputLocation = inputLocations.get(output)
            if outputLocation is None:
                graphNodes[curCurId].outputs.append(createFinalOutputShape([curCurId],outputShapeCode,output))
            else:
                curId = newId()
                graphNodes[curId] = GraphNode(GraphNode.SHAPE,[curCurId],None,
                    renderShape(outputShapeCode),output,outputShapeCode)
                graphNodes[curCurId].outputs.append(curId)
                toGenOutputs.append((curId,outputLocation))
        for cid,ol in toGenOutputs:
            graphNodes[cid].outputs = [genGraphNode(instructions[ol],ol)]

        return curCurId

    try:
        for i,instruction in enumerate(instructions):
            genGraphNode(instruction,i)
    except shapeOperations.InvalidOperationInputs as e:
        return False,f"Error happened somewhere : {e}"
    except RecursionError:
        return False,f"Too many connected instructions"

    def getNodeLayer(node:GraphNode) -> int:
        if node.layer is None:
            if node.inputs is None:
                node.layer = 0
            else:
                node.layer = max(getNodeLayer(graphNodes[n]) for n in node.inputs)+1
        return node.layer

    for node in graphNodes.values():
        getNodeLayer(node)

    maxNodeLayer = max(n.layer for n in graphNodes.values())
    for node in graphNodes.values():
        if node.outputs is None:
            node.layer = maxNodeLayer

    graphNodesLayers:dict[int,dict[int,GraphNode]] = {}
    for nodeId,node in graphNodes.items():
        if graphNodesLayers.get(node.layer) is None:
            graphNodesLayers[node.layer] = {}
        graphNodesLayers[node.layer][nodeId] = node

    maxNodesPerLayer = max(len(l) for l in graphNodesLayers.values())
    graphWidth = round((maxNodesPerLayer*GRAPH_NODE_SIZE)+((maxNodesPerLayer-1)*GRAPH_H_MARGIN))
    graphHeight = round(((maxNodeLayer+1)*GRAPH_NODE_SIZE)+(maxNodeLayer*GRAPH_V_MARGIN))

    for layerIndex,layer in graphNodesLayers.items():
        layerLen = len(layer)
        layerWidth = (layerLen*GRAPH_NODE_SIZE)+((layerLen-1)*GRAPH_H_MARGIN)
        for nodeIndex,node in enumerate(layer.values()):
            node.pos = (((graphWidth-layerWidth)/2)+(nodeIndex*(GRAPH_NODE_SIZE+GRAPH_H_MARGIN)),
                layerIndex*(GRAPH_NODE_SIZE+GRAPH_V_MARGIN))

    graphSurface = pygame.Surface((graphWidth,graphHeight),pygame.SRCALPHA)

    for node in graphNodes.values():
        if node.outputs is not None:
            for output in node.outputs:
                outputPos = graphNodes[output].pos
                pygame.draw.line(graphSurface,LINE_COLOR,
                    (node.pos[0]+(GRAPH_NODE_SIZE/2),node.pos[1]+GRAPH_NODE_SIZE),
                    (outputPos[0]+(GRAPH_NODE_SIZE/2),outputPos[1]),LINE_WIDTH)

    shapeVarValues = {}

    for node in graphNodes.values():
        graphSurface.blit(node.image,node.pos)
        if node.type == GraphNode.SHAPE:
            shapeVarValues[node.shapeVar] = node.shapeCode
            if showShapeVars:
                varText = SHAPE_VAR_FONT.render(str(node.shapeVar),1,SHAPE_VAR_COLOR)
                graphSurface.blit(varText,(node.pos[0]+GRAPH_NODE_SIZE-varText.get_width(),
                    node.pos[1]+GRAPH_NODE_SIZE-varText.get_height()))

    with io.BytesIO() as buffer:
        pygame.image.save(graphSurface,buffer,"png")
        graphImage = io.BytesIO(buffer.getvalue())

    return True,(graphImage,shapeVarValues)
import shapeOperations
import shapeCodeGenerator
import globalInfos
import pygame

class Operation:

    def __init__(self,numInputs:int,numOutputs:int,fullName:str,func,colorInputIndexes:list[int]|None=None) -> None:
        self.numInputs = numInputs
        self.numOutputs = numOutputs
        self.fullName = fullName
        self.func = func
        self.colorInputindexes = colorInputIndexes
        self.image = None

class Instruction:

    DEF = "def"
    OP = "op"

    def __init__(self,type:str,*,shapeVars:list[int]|None=None,shapeCodes:list[str]|None=None,
            inputShapeVars:list[int]|None=None,operation:Operation|None=None,outputShapeVars:list[int]|None=None) -> None:
        self.type = type
        if type == Instruction.DEF:
            self.vars = shapeVars
            self.shapeCodes = shapeCodes
        else:
            self.inputs = inputShapeVars
            self.op = operation
            self.outputs = outputShapeVars

IMAGES_START_PATH = "./operationGraphImages/"
OPERATIONS:dict[str,Operation] = {
    "cut" : Operation(1,2,"Cut",shapeOperations.cut),
    "hcut" : Operation(1,1,"Half cut",shapeOperations.halfCut),
    "r90CW" : Operation(1,1,"Rotate 90° clockwise",shapeOperations.rotate90CW),
    "r90CCW" : Operation(1,1,"Rotate 90° counterclockwise",shapeOperations.rotate90CCW),
    "r180" : Operation(1,1,"Rotate 180°",shapeOperations.rotate180),
    "sh" : Operation(2,2,"Swap halves",shapeOperations.swapHalves),
    "stack" : Operation(2,1,"Stack",shapeOperations.stack),
    "paint" : Operation(2,1,"Paint",shapeOperations.topPaint,[1]),
    "pin" : Operation(1,1,"Push pin",shapeOperations.pushPin),
    "crystal" : Operation(2,1,"Generate crystals",shapeOperations.genCrystal,[1])
}

for k,v in OPERATIONS.items():
    v.image = pygame.image.load(f"{IMAGES_START_PATH}{k}.png")

def getInstructionsFromText(text:str) -> tuple[bool,list[Instruction]|str]:
    def decodeInstruction(instruction:str) -> tuple[bool,str|Instruction]:
        if "=" in instruction:
            if instruction.count("=") > 1:
                return False,"Max 1 '=' per instruction"
            shapeVars, shapeCode = instruction.split("=")
            if shapeVars == "":
                return False,"Empty variables section"
            if shapeCode == "":
                return False,"Empty shape code section"
            shapeVars = shapeVars.split(",")
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
        else:
            if instruction.count(":") != 2:
                return False,"Operation instruction must contain 2 ':'"
            inputs, op, outputs = instruction.split(":")
            for k,v in {"inputs":inputs,"operation":op,"outputs":outputs}.items():
                if v == "":
                    return False,f"Empty {k} section"
            if OPERATIONS.get(op) is None:
                return False,f"Unknown operation '{op}'"
            inputs = [i.replace("m","p") for i in inputs.split(",")]
            outputs = outputs.split(",")
            inputsInt = []
            outputsInt = []
            curOperation = OPERATIONS.get(op)
            for i,input in enumerate(inputs):
                if i in curOperation.colorInputindexes:
                    if input not in globalInfos.SHAPE_COLORS:
                        return False,f"Input {i+1} msut be a color"
                else:
                    try:
                        inputsInt.append(int(input))
                    except ValueError:
                        return False,f"Input {i+1} not an integer"
            for i,output in enumerate(inputs):
                try:
                    outputsInt.append(int(output))
                except ValueError:
                    return False,f"Output {i+1} not an integer"
            for e,g,t in zip((curOperation.numInputs,curOperation.numOutputs),(len(inputsInt),len(outputsInt)),("inputs","outputs")):
                if e != g:
                    return False,f"Number of operation {t} isn't the same as number of {t} given ({e} vs {g})"
            return True,Instruction(Instruction.OP,inputShapeVars=inputsInt,operation=curOperation,outputShapeVars=outputsInt)
    if text == "":
        return False,"Empty text"
    instructions = text.split(";")
    decodedInstructions = []
    for i,instruction in enumerate(instructions):
        valid, decodedInstructionOrError = decodeInstruction(instruction)
        if not valid:
            return False,f"Error in instruction {i+1} : {decodedInstructionOrError}"
        decodedInstructions.append(decodedInstructionOrError)
    return True,decodedInstructions

def genOperationGraph(instructions:list):
    pass
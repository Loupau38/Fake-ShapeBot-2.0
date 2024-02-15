import gameInfos
import shapeViewer
import utils
import pygame
import io

BG_COLOR = (40,60,82)
LEVEL_COLOR = (23,42,60)
NODE_COLOR = (29,54,74)
TEXT_COLOR = (255,255,255)

pygame.font.init()
VERSION_FONT = pygame.font.SysFont("arial",10,True)
NODE_FONT = pygame.font.SysFont("arial",30)
NODE_FONT_BOLD = pygame.font.SysFont("arial",30,True)

SHAPE_SIZE = 100
RECT_BORDER_RADIUS = 30
MARGIN = 5

def preRenderAllNames() -> tuple[dict[str,pygame.Surface],int]:
    nodeNames:dict[str,pygame.Surface] = {}
    for lvl in gameInfos.research.reserachTree:
        for n in [lvl.milestone,*lvl.sideGoals]:
            nodeNames[n.id] = utils.decodedFormatToPygameSurf(utils.decodeUnityFormat(n.title),NODE_FONT,NODE_FONT_BOLD,1,TEXT_COLOR)
    return nodeNames, SHAPE_SIZE+max(n.get_width() for n in nodeNames.values())+MARGIN

_preRenderedNodeNames, _nodeWidth = preRenderAllNames()
_nodeHeight = SHAPE_SIZE
_maxSideGoalsInLevel = max(len(lvl.sideGoals) for lvl in gameInfos.research.reserachTree)
_levelNumMaxHeight = max(NODE_FONT.render(str(num),1,TEXT_COLOR).get_height() for num in range(1,len(gameInfos.research.reserachTree)+1))
_levelWidth = _nodeWidth + (2*MARGIN)
_levelHeight = MARGIN + _levelNumMaxHeight + MARGIN + _nodeHeight + (3*MARGIN) + ((_nodeHeight+MARGIN)*_maxSideGoalsInLevel)
_numLevels = len(gameInfos.research.reserachTree)
_treeWidth = (_numLevels*_levelWidth) + ((_numLevels-1)*MARGIN)
_treeHeight = _levelHeight

_treeCache:tuple[bytes,int]|None = None

def _renderNode(node:gameInfos.research.Node) -> pygame.Surface:
    nodeSurf = pygame.Surface((_nodeWidth,_nodeHeight),pygame.SRCALPHA)
    pygame.draw.rect(nodeSurf,NODE_COLOR,pygame.Rect(0,0,*nodeSurf.get_size()),border_radius=RECT_BORDER_RADIUS)
    nodeSurf.blit(shapeViewer.renderShape(node.goalShape,SHAPE_SIZE),(0,0))
    nodeName = _preRenderedNodeNames[node.id]
    nodeSurf.blit(nodeName,(SHAPE_SIZE,(nodeSurf.get_height()/2)-(nodeName.get_height()/2)))
    return nodeSurf

def _renderLevel(level:gameInfos.research.Level) -> pygame.Surface:
    levelSurf = pygame.Surface((_levelWidth,_levelHeight),pygame.SRCALPHA)
    pygame.draw.rect(levelSurf,LEVEL_COLOR,pygame.Rect(0,0,*levelSurf.get_size()),border_radius=RECT_BORDER_RADIUS)
    curY = MARGIN
    levelNum = NODE_FONT.render(str(gameInfos.research.reserachTree.index(level)+1),1,TEXT_COLOR)
    levelSurf.blit(levelNum,((levelSurf.get_width()/2)-(levelNum.get_width()/2),curY))
    curY += levelNum.get_height() + MARGIN
    for i,node in enumerate([level.milestone,*level.sideGoals]):
        renderedNode = _renderNode(node)
        levelSurf.blit(renderedNode,(MARGIN,curY))
        curY += renderedNode.get_height() + MARGIN + ((2*MARGIN) if i == 0 else 0)
    return levelSurf

def _renderTree() -> pygame.Surface:
    treeSurf = pygame.Surface((_treeWidth,_treeHeight))
    treeSurf.fill(BG_COLOR)
    curX = 0
    for level in gameInfos.research.reserachTree:
        renderedLevel = _renderLevel(level)
        treeSurf.blit(renderedLevel,(curX,0))
        curX += renderedLevel.get_width() + MARGIN
    return treeSurf

def _showSurface(surf:pygame.Surface) -> pygame.Surface:
    newSurf = pygame.Surface((surf.get_width()+30,surf.get_height()+30))
    newSurf.fill(BG_COLOR)
    newSurf.blit(surf,(15,15))
    versionText = VERSION_FONT.render(gameInfos.research.treeVersion,1,TEXT_COLOR)
    newSurf.blit(versionText,(0,newSurf.get_height()-versionText.get_height()))
    return newSurf

def renderTree() -> tuple[io.BytesIO,int]:
    global _treeCache
    if _treeCache is None:
        image, imageSize = utils.pygameSurfToBytes(_showSurface(_renderTree()))
        _treeCache = (image.getvalue(),imageSize)
    image, imageSize = _treeCache
    return io.BytesIO(image), imageSize

def renderLevel(level:int) -> tuple[io.BytesIO,int]:
    return utils.pygameSurfToBytes(_showSurface(_renderLevel(gameInfos.research.reserachTree[level])))

def renderNode(level:int,node:int) -> tuple[io.BytesIO,int]:
    return utils.pygameSurfToBytes(_showSurface(_renderNode(
        gameInfos.research.reserachTree[level].milestone if node == 0 else gameInfos.research.reserachTree[level].sideGoals[node-1])))
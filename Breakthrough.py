import pygame, sys, os, shutil, sPickle, time, ast
from pygame.locals import *
from random import randint
from numpy import *

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255,   0)
GRAY = (128, 128, 128)

boardsize = (8, 8)
windowsize = (800, 800)
figuresize = (50, 50)
tilesize =  (windowsize[0] / boardsize[0], windowsize[1] / boardsize[1])
figureFileName = 'figures'
player1Sign = 1
player2Sign = 2
emptySign = 0
selectedSign1 = 3
selectedSign2 = 4
defaultFigurePositions = array([[player1Sign]*8, [player1Sign]*8, [emptySign]*8, [emptySign]*8, [emptySign]*8, [emptySign]*8, [player2Sign]*8, [player2Sign]*8])
targetFigurePresent = False

def switchplayer(player):
    if player == player1Sign:
        return player2Sign
    if player == player2Sign:
        return player1Sign

def dorandomlegalmove(figurepositions, player):
    #print(player)
    possiblemoves = dictlegalmovesbyplayer(figurepositions, player)
    figuresthathavemoves = possiblemoves.keys()
    numfiguresthathavemoves = len(figuresthathavemoves)
    origin = ast.literal_eval(figuresthathavemoves[randint(0, numfiguresthathavemoves-1)])
    possibledestinations = possiblemoves[str(origin)]
    destination = possibledestinations[randint(0, len(possibledestinations)-1)]
    return makemove(figurepositions, origin, destination)

def dictlegalmovesbyplayer(figurepositions, player):
    locations = dictfigures(figurepositions, player)
    moves = {}
    if player == player1Sign: ychange = 1 # player 1 can only move down
    else: ychange = -1
    for pos in locations[str(player)]:
        moves[str(pos)] = []
        for xchange in range(-1,2):
            if islegalmove(figurepositions, pos, [pos[0]+xchange, pos[1] + ychange]):
                moves[str(pos)].append([pos[0]+xchange, pos[1] + ychange])
        if moves[str(pos)] == []:
            del(moves[str(pos)])
    return moves

def dictlegalmovesbyfigure(figurepositions, fpos):
    return dictlegalmovesbyplayer(figurepositions, figurepositions[fpos[1]][fpos[0]])[str(fpos)]

def iswon(figurepositions):
    # figurepositions = figurepositions.astype(int)
    if (player1Sign in figurepositions[-1]) or (sum(sum(figurepositions == player2Sign)) == 0):
    # if (player1Sign in figurepositions[-1]):
        return player1Sign
    elif (player2Sign in figurepositions[0]) or (sum(sum(figurepositions == player1Sign)) == 0):
    # elif (player2Sign in figurepositions[0]):
        return player2Sign
    return False

def iswon2(figurepositions):
    # figurepositions = figurepositions.astype(int)
    # if (1 in figurepositions[-1]) or (sum(sum(figurepositions == -1)) == 0):
    if (1 in figurepositions[-1]):
        return player1Sign
    # elif (-1 in figurepositions[0]) or (sum(sum(figurepositions == 1)) == 0):
    elif (-1 in figurepositions[0]):
        return player2Sign
    return False

def iswon3(figurepositions):
    # figurepositions = figurepositions.astype(int)
    if (1 in figurepositions[-1]) or (sum(sum(figurepositions == -1)) == 0):
    # if (1 in figurepositions[-1]):
        return player1Sign
    elif (-1 in figurepositions[0]) or (sum(sum(figurepositions == 1)) == 0):
    # elif (-1 in figurepositions[0]):
        return player2Sign
    return False

def deselectAll(figurepositions):
    global targetFigurePresent
    targetFigurePresent = False
    for x in range(boardsize[0]):
        for y in range(boardsize[1]):
            if figurepositions[y][x] == selectedSign1:
                figurepositions[y][x] = player1Sign
            elif figurepositions[y][x] == selectedSign2:
                figurepositions[y][x] = player2Sign
    return figurepositions

def isselected(figurepositions, fpos):
    return figurepositions[fpos[1]][fpos[0]] == selectedSign1 or figurepositions[fpos[1]][fpos[0]] == selectedSign2

def deselect(figurepositions, fpos):
    global targetFigurePresent
    if figurepositions[fpos[1]][fpos[0]] == selectedSign1:
        figurepositions[fpos[1]][fpos[0]] = player1Sign
        targetFigurePresent = False
    elif figurepositions[fpos[1]][fpos[0]] == selectedSign2:
        figurepositions[fpos[1]][fpos[0]] = player2Sign
        targetFigurePresent = False
    elif figurepositions[fpos[1]][fpos[0]] == emptySign:
        print('Given field was empty')
    else:
        print('Given field was not selected')
    return figurepositions

def select(figurepositions, fpos):
    global targetFigurePresent
    figurepositions = deselectAll(figurepositions)
    if figurepositions[fpos[1]][fpos[0]] == player1Sign:
        targetFigurePresent = fpos
        figurepositions[fpos[1]][fpos[0]] = selectedSign1
    elif figurepositions[fpos[1]][fpos[0]] == player2Sign:
        targetFigurePresent = fpos
        figurepositions[fpos[1]][fpos[0]] = selectedSign2
    elif figurepositions[fpos[1]][fpos[0]] == emptySign:
        print('Given field was empty')
    else:
        print('Given field was already selected')
    return figurepositions

def dictfigures(figurepositions, player):
    if player == 'both':
        figureDict = {str(player1Sign): [], str(player2Sign): []}
        for x in range(boardsize[0]):
            for y in range(boardsize[1]):
                if figurepositions[y][x] == player1Sign or figurepositions[y][x] == player2Sign:
                    #figureDict[str([x, y])] = figurepositions[y][x]
                    figureDict[str(figurepositions[y][x])].append([x, y])
    elif player == player1Sign:
        figureDict = {str(player1Sign): []}
        for x in range(boardsize[0]):
            for y in range(boardsize[1]):
                if figurepositions[y][x] == player1Sign:
                    #figureDict[str([x, y])] = figurepositions[y][x]
                    figureDict[str(figurepositions[y][x])].append([x, y])
    elif player == player2Sign:
        figureDict = {str(player2Sign): []}
        for x in range(boardsize[0]):
            for y in range(boardsize[1]):
                if figurepositions[y][x] == player2Sign:
                    #figureDict[str([x, y])] = figurepositions[y][x]
                    figureDict[str(figurepositions[y][x])].append([x, y])
    return figureDict

def makemove(figurepositions, origin, destination, dA = True):
    if dA:
        figurepositions = deselectAll(figurepositions)
    xOrigin = origin[0]
    yOrigin = origin[1]
    xDestinantion = destination[0]
    yDestinantion = destination[1]
    figuresign = figurepositions[yOrigin][xOrigin]
    figurepositions[yOrigin][xOrigin] = emptySign
    figurepositions[yDestinantion][xDestinantion] = figuresign
    #writefigurepositions(figureFileName, figurepositions)
    return figurepositions

def islegalmove(figurepositions, origin, destination, precheck = False):
    #figurepositions = deselectAll(figurepositions)
    xOrigin = origin[0]
    yOrigin = origin[1]
    xDestinantion = destination[0]
    yDestinantion = destination[1]
    global targetFigurePresent
    targetFigurePresent = origin
    figuresign = figurepositions[yOrigin][xOrigin]
    if figuresign == 0:
        return False
    if xDestinantion > boardsize[0]-1 or xDestinantion < 0:
        return False
    if yDestinantion > boardsize[1]-1 or yDestinantion < 0:
        return False
    destinationsign = figurepositions[yDestinantion][xDestinantion]
    if precheck == False:
        if origin == destination:
            return False
        if abs(xOrigin - xDestinantion) > 1:
            return False
        if abs(yOrigin - yDestinantion) > 1:
            return False
        if figuresign == player1Sign:
            if yOrigin >= yDestinantion:
                return False
        if figuresign == player2Sign:
            if yOrigin <= yDestinantion:
                return False
    if destinationsign == figuresign:
        return False
    if destinationsign == switchplayer(figuresign):
        if xOrigin == xDestinantion:
            return False
    return True

def mouse2FigurePos(figurepositions, mpos):
    fpos = []
    for x in range(1, boardsize[0]+1):
        if mpos[0] < x * tilesize[0]:
            fpos.append(x-1)
            break
    for y in range(1, boardsize[1]+1):
        if mpos[1] < y * tilesize[1]:
            fpos.append(y-1)
            break
    return fpos

def drawfigures(figurepositions, surface):
    for x in range(boardsize[0]):
        for y in range(boardsize[1]):
            if figurepositions[y][x] == player1Sign:
                pygame.draw.rect(surface, BLACK, (x * tilesize[0] + (tilesize[0] - figuresize[0]) // 2, y * tilesize[1]
                                                   + (tilesize[1] - figuresize[1]) // 2, figuresize[0], figuresize[1]))
            elif figurepositions[y][x] == player2Sign:
                pygame.draw.rect(surface, YELLOW, (x * tilesize[0] + (tilesize[0] - figuresize[0]) // 2, y * tilesize[1]
                                                  + (tilesize[1] - figuresize[1]) // 2, figuresize[0], figuresize[1]))
            elif figurepositions[y][x] == selectedSign1 or figurepositions[y][x] == selectedSign2:
                pygame.draw.rect(surface, GREEN, (x * tilesize[0] + (tilesize[0] - figuresize[0]) // 2, y * tilesize[1]
                                                  + (tilesize[1] - figuresize[1]) // 2, figuresize[0], figuresize[1]))

def readfigurepositions(fname):
    filedir = os.getcwd() + '\\' + fname
    copydir = filedir + '-copy'
    shutil.copy(filedir, copydir)
    copyname = fname + '-copy'
    f = open(copyname)
    pos = array(list(sPickle.s_load(f)))
    f.close()
    return pos

def writefigurepositions(fname, positions):
    f = open(fname, 'wb')
    sPickle.s_dump(positions, f)
    f.close()

def initializeboard(windowSurface):

    windowSurface.fill(WHITE)

    # set up fonts
    basicFont = pygame.font.SysFont(None, 48)

    for x in range(boardsize[0]): # Create Tiles
        for y in range(boardsize[1]):
            colorvar = y+x+2
            if colorvar % 2 != 0:
                TILECOLOR = GRAY
            else:
                TILECOLOR = WHITE
            pygame.draw.rect(windowSurface, TILECOLOR, (x * tilesize[0], y * tilesize[1], tilesize[0], tilesize[1]))


def main():
    # set up pygame
    pygame.init()
    # set up the window
    windowSurface = pygame.display.set_mode(windowsize, 0, 32)
    pygame.display.set_caption('Breakthrough')
    writefigurepositions(figureFileName, defaultFigurePositions)
    turn = player1Sign #remove
    won = False
    # run the game loop
    while True:
        #turn = switchplayer(turn)#remove
        #currentFigurePositions = readfigurepositions(figureFileName)
        #won = iswon(currentFigurePositions)
        try:
            currentFigurePositions = readfigurepositions('currentgame')
            loadedproperly = False
            while loadedproperly == False:
                try:
                    currentFigurePositions[7][7]
                    loadedproperly = True
                except:
                    currentFigurePositions = readfigurepositions('currentgame')
                    loadedproperly = False
        except:
            pass
        #currentFigurePositions = readfigurepositions(figureFileName) #ownplay
        if won !=False:
            print('Player '+str(won)+' has won!')
            pygame.quit()
            sys.exit()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_q:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                target = mouse2FigurePos(currentFigurePositions, pygame.mouse.get_pos())
                #print(target)# @debug
                #print(dictlegalmovesbyfigure(currentFigurePositions, target))# @debug
                #currentFigurePositions = dorandomlegalmove(currentFigurePositions, currentFigurePositions[target[1]][target[0]])

                if isselected(currentFigurePositions, target):
                    #print('was sel')# @debug
                    currentFigurePositions = deselect(currentFigurePositions, target)
                else:
                    if targetFigurePresent == False:
                       # print('no target figure present')# @debug
                        currentFigurePositions = select(currentFigurePositions, target)
                    else:
                        #print('tfp and it is') # @debug
                        if islegalmove(currentFigurePositions, targetFigurePresent, target):
                            currentFigurePositions = makemove(currentFigurePositions, targetFigurePresent, target)
                        else:
                            print('move not legal')
                            currentFigurePositions = deselectAll(currentFigurePositions)
                #print(targetFigurePresent)# @debug


        initializeboard(windowSurface)
        drawfigures(currentFigurePositions, windowSurface)

        pygame.display.update()

        #writefigurepositions(figureFileName, currentFigurePositions) #ownplay
        time.sleep(0.1)


if __name__ == "__main__":
    main()

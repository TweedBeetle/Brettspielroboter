from featurecomputation import *
from Breakthrough import *
from operator import itemgetter
from NeuralNetwork import *
from numpy.lib.stride_tricks import as_strided
import threading
import Queue
import time
import multiprocessing as mp
import UCT

# an ai is structured as follows:
# numpy matrix. ai[i] = weight the ai gives the heuristic number i. no player indication means own. no row indication means whole board. # = number of
# [#pieces #moves #takes #safe1 #safe2 #unsafe #piecesenemy #movesenemy #takesenemy #safe1enemy #safe2enemy #unsafeenemy]
# for each item in the array above there are also 2 variables c_featurebyrow and a_featurebyrow .: c_movesbyrow, a_movesbyrow.
# all these are used in the heuristic score calculation as follows:
# score = ai[0] * numpieces + ai[1] * nummoves etc... + c_movesbyrow * a_movesbyrow**(row) etc...

def splitlist(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]

def nnboard(board, player):
    if player == 1: # change to 2
        board = turntables(board)
    board[board == 1] = -1
    board[board == 2] = 1
    return board.reshape(1, 64)[0]

def nnboard2(board, player):
    b = copy(board)
    b[b == player] = 1
    b[b == other(player)] = -1
    return b.reshape(1, 64)[0]

def nnboard3(board, player):
    b = copy(board)
    if player == 1:
        b = turntables(b)
    b[b == 1] = -1
    b[b == 2] = 1
    nnb = b.reshape(1, 64)[0]
    nps = array([0]*8)
    for i in range(8):
        nps[i] = sum(b[i,:])
    return concatenate((nnb, nps, array([dsum(nnb[nnb == 1]), dsum(nnb[nnb == -1])])))

def nnboard4(board, player):
    if player == 2:
        board = turntables(board)
    board[board == 2] = -1
    b = zeros((91,64))
    c = 0
    for subs in range(3,9):
        nsubsperrow = 9 - subs
        subvectorlength = subs**2
        for row in range(nsubsperrow):
            for column in range(nsubsperrow):
                subboard = board[row:row+subs,column:column+subs]
                b[c,0:subvectorlength] = reshape(subboard, (1, subvectorlength))
                c += 1
    return b

def nnboard5(board, player):
    board[board == other(player)] = -1
    if player == 2:
        board[board == player] = 1
    x = zeros((91,64))
    for subs in range(3,4):
        sub_shape = (subs, subs)
        view_shape = tuple(subtract(board.shape, sub_shape) + 1) + sub_shape
        arr_view = as_strided(board, view_shape, board.strides * 2)
        arr_view = arr_view.reshape((-1,) + sub_shape)
        x = array([reshape(subm, (1, len(subm)**2))[0] for subm in arr_view])
    return x

def nnboard6(board, player):
    o = other(player)
    board[board == o] = -1
    if player == 2:
        board[board == player] = 1
    return board.reshape(1, 64)[0]

def fastboard(board, player):
    # return concatenate([board.reshape(1, 64)[0], [player]])
    if player == 1:
        return board.reshape(1, 64)[0]
    else:
        return (board * -1).reshape(1, 64)[0]

def nn88board(board):
    board[board == 2] = -1
    return board

def normalboard(board):
    board[board == -1] = 2
    return board

def mirror(board):
    return fliplr(flipud(board))

def turntablesold(board):
    board = mirror(board)
    board[board == 1] = 5
    board[board == 2] = 1
    board[board == 5] = 2
    return board

def turntables(board):
    board = mirror(board)
    board *= 2
    board[board == 4] = 1
    return board

def subjectiveboard(board, player):
    if player == 2:
        return  board
    elif player == 1:
        return turntables(board)
    else:
        print("player not recognised in subjectiveboard")

def dsum(a):
    # return sum(sum(a))
    return a.sum()

def msum(a):
    shape = a.shape
    return sum(reshape(a, (1, shape[0] * shape[1]))[0])

def makemove2(board, origin, destination):
    temp = copy(board)
    temp[destination[1],destination[0]] = board[origin[1],origin[0]]
    temp[origin[1],origin[0]] = 0.
    return temp

def makemove4(board, pos, verbose = False):
    origin = [pos[0], pos[1]]
    destination = [pos[2], pos[3]]
    if verbose:
        print(pos)
        print(origin)
        print(destination)
        print('____________')
    temp = copy(board[:])
    temp[destination[0],destination[1]] = board[origin[0],origin[1]]
    temp[origin[0],origin[1]] = 0.
    return temp

def makemove3(temp, origin, destination):
    temp[destination[1],destination[0]] = temp[origin[1],origin[0]]
    temp[origin[1],origin[0]] = 0.
    return temp

def scoreold1(board, player, ai):
    points = 0.0
    staticvars = matrix(zeros((1, 12)))
    staticvars[0,0:6] = array([numpieces(board, player), nummoves(board, player), numtakes(board, player), numsafe(board, player, 1), numsafe(board, player, 2), numunsafe(board, player)])
    player = other(player)
    staticvars[0,6:12] = array([numpieces(board, player), nummoves(board, player), numtakes(board, player), numsafe(board, player, 1), numsafe(board, player, 2), numunsafe(board, player)])
    points += staticvars * ai[0:12]

    features = [numpieces, nummoves, numtakes, numsafedegree1, numsafedegree2, numunsafe]
    scalingvars = matrix(zeros((96, 1)))
    player = other(player)
    c = zeros((12, 1))
    a = zeros((12, 1))
    for index, value in enumerate(range(12,36,2)):
        c[index] = ai[value]
        a[index] = ai[value+1]
    for i in range(2):
        for featureindex, feature in enumerate(features):
            for row in range(8):
                scalingvars[(i * 48) + (featureindex * 8) + row] = (c[i * 6 + featureindex] * a[i * 6 + featureindex] ** row) * feature(board, player, row)
        player = other(player)
    return float(points + sum(scalingvars))

def score(board, player, ai):
    points = 0.0
    enemy = other(player)

    pieces = numpieces2(board, player)
    moves = nummoves2(board, player)
    takes = numtakes2(board, player)
    safe = numsafe2(board, player)
    unsafe = numunsafe2(board, player)

    enemypieces = numpieces2(board, enemy)
    enemymoves = nummoves2(board, enemy)
    enemytakes = numtakes2(board, enemy)
    enemysafe = numsafe2(board, enemy)
    enemyunsafe = numunsafe2(board, enemy)

    staticvars = array([dsum(pieces), dsum(moves), dsum(takes), dsum(safe), dsum(unsafe), dsum(enemypieces), dsum(enemymoves), dsum(enemytakes), dsum(enemysafe), dsum(enemyunsafe)])

    points += staticvars * ai[0:10]
    features = [pieces, moves, takes, safe, unsafe, enemypieces, enemymoves, enemytakes, enemysafe, enemyunsafe]
    scalingvars = matrix(zeros((160, 1)))
    player = other(player)
    c = zeros((30, 1))
    a = zeros((30, 1))
    b = zeros((20, 1))
    for index, value in enumerate(range(10,70,2)):
        c[index] = ai[value]
        a[index] = ai[value+1]
    for index, value in enumerate(range(70,90)):
        b[index] = ai[value]
    for featureindex, feature in enumerate(features):
        for row in xrange(8):
            scalingvars[featureindex * 8 + row] = (c[featureindex] * (row - 3.5) ** round(b[featureindex]) + a[featureindex]) * sum(feature[row])
    for featureindex, feature in enumerate(features):
        for column in xrange(8):
            scalingvars[80 + featureindex * 8 + column] = (c[featureindex + 10] * (column - 3.5) ** 2 + a[featureindex + 10]) * sum(feature[:,column])
    points += sum(scalingvars)
    scalingvarsrowdifference = zeros((40,1))
    for index in xrange(5):
        for row in xrange(8):
            scalingvarsrowdifference[index * 8 + row] = (c[index + 20] * (row - 3.5) ** round(b[index + 10]) + a[index + 20]) * (scalingvars[index * 8 + row] - scalingvars[40 + index * 8 + row])
    scalingvarscolumndifference = zeros((40,1))
    for index in xrange(5):
        for column in xrange(8):
            scalingvarscolumndifference[index * 8 + column] = (c[index + 25] * (column - 3.5) ** round(b[index + 15]) + a[index + 25]) * (scalingvars[80 + index * 8 + column] - scalingvars[120 + index * 8 + column])

    staticdifference = (staticvars[0:5] - staticvars[5:10]) * ai[90:95]

    points += sum(scalingvarscolumndifference) + sum(scalingvarsrowdifference)

    return float(points)

def nnscore(board, player, ai):
    sboard = board.copy()
    sboard = subjectiveboard(sboard, player)
    sboard[sboard == 2] = 1
    sboard[sboard == 1] = -1
    return float(predict2(ai, sboard.reshape(1,64)[0]))

def bestboards(boards, player, ai, num):
    lenboards = len(boards)
    if num > lenboards:
        num = lenboards
    scores = [0] * lenboards
    best = array([zeros((8,8))]*num)
    for index, board in enumerate(boards):
        scores[index] = [score(board, player, ai), index]
    scores = sorted(scores, key=itemgetter(0))
    for i in xrange(num):
        best[i] = boards[scores.pop()[1]]
    return best

def getnextstates(board, player): # deprecated
    board = board.astype(int)
    numpossiblemoves = nummoves(board, player)
    possiblemoves = dictlegalmovesbyplayer(board, player)
    figuresthathavemoves = possiblemoves.keys()
    numfiguresthathavemoves = len(figuresthathavemoves)
    states =  array([[zeros((8,8))]*numpossiblemoves])
    counter = 0
    for origin in figuresthathavemoves:
        for destination in possiblemoves[origin]:
            states[0,counter] = makemove2(board, ast.literal_eval(origin), destination)
            counter += 1
    return states

def getnextstates2(board, player):
    # board = board.astype(int)
    states = []
    if player == 1:
        for y in xrange(7):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y+1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y+1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y+1]))
                        states.append(copy(board))
                        states[-1][y+1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    elif player == 2:
        for y in xrange(1,8):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y-1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y-1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y-1]))
                        states.append(copy(board))
                        states[-1][y-1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    return states

def getnextstates3(board, player):
    board = board.astype(int)
    states = []
    if player == 1:
        playerymodi = 1
    elif player == 2:
        playerymodi = -1
    positions = where(board == player)

    for posnum in range(len(positions[0])):
        x = positions[1][posnum]
        y = positions[0][posnum]
        for xdistance in range(-1,2,1):
            if islegalmove(board, [x, y], [(x + xdistance), y+playerymodi], True):
                states.append(makemove2(board, [x, y], [(x + xdistance), y+playerymodi]))
    states = array(states)
    return states

def getnnnextstates(board, player):
    # board = board.astype(int)
    states = []
    if player == 1:
        for y in xrange(7):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y+1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y+1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y+1]))
                        states.append(copy(board))
                        states[-1][y+1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    elif player == 2:
        player = -1
        for y in xrange(1,8):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y-1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y-1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y-1]))
                        states.append(copy(board))
                        states[-1][y-1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    return states

def getRowNextStates(args):
    board, player, rows = args[0], args[1], args[2]
    states = []
    if player == 1:
        for y in rows:
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y+1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y+1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y+1]))
                        states.append(copy(board))
                        states[-1][y+1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    elif player == 2:
        player = -1
        for y in rows:
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y-1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y-1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y-1]))
                        states.append(copy(board))
                        states[-1][y-1, (x + xdistance)] = player
                        states[-1][y, x] = 0
    if states != []:
        # lock.acquire()
        return states
        # lock.release()
        # q.put(states)
    # print('done!')
    return

def ThreadedGetNNNextStates(board, player):
    threadnum = 4
    # lock = threading.Lock()
    lock = 0
    # q = Queue.Queue()
    if player == 1:
        yrange = range(7)
    elif player == 2:
        yrange = range(1, 8)

    ys = splitlist(yrange, threadnum)
    arguments = []
    for i in range(threadnum):
        arguments.append([board, player, ys[i]])

    pool = mp.Pool()
    allstates = pool.map(getRowNextStates, arguments)

    # for y in splitlist(yrange, threadnum):
    #     t = threading.Thread(target=getRowNextStates, args=(board, player, y, lock, allstates))
    #     t.start()
    # main_thread = threading.currentThread()
    # for t in threading.enumerate():
    #     if t is not main_thread:
    #         t.join()
    #
    # while threading.active_count() > 1:
    #     time.sleep(0.001)

    # while not q.empty():
    #     allstates.append(q.get())
    print(allstates[0])
    if len(allstates) == 1:
        return allstates[0]
    if len(allstates) == 0:
        return []
    return concatenate(array(allstates))

def getnnnextstates2(board, player, num):
    # board = board.astype(int)
    states = []
    c = 0
    if player == 1:
        for y in xrange(7):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y+1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y+1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y+1]))
                        states.append(copy(board))
                        states[-1][y+1, (x + xdistance)] = player
                        states[-1][y, x] = 0
                        c += 1
                        if c == num:
                            return states
    elif player == 2:
        player = -1
        for y in xrange(1,8):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y-1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y-1 ,x+xdistance] != 0:
                                continue
                        # states.append(makemove2(board, [x, y], [(x + xdistance), y-1]))
                        states.append(copy(board))
                        states[-1][y-1, (x + xdistance)] = player
                        states[-1][y, x] = 0
                        c += 1
                        if c == num:
                            return states
    return states

def GetNextMoves(board, player):
    # board = board.astype(int)
    moves = []
    if player == 1:
        for y in xrange(7):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y+1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y+1 ,x+xdistance] != 0:
                                continue
                        start = [y, x]
                        end = [y+1, x + xdistance]
                        # moves.append([start, end])
                        moves.append([start[0], start[1], end[0], end[1]])
    elif player == 2:
        player = -1
        for y in xrange(1,8):
            for x in xrange(8):
                if board[y,x] == player:
                    for xdistance in range(-1,2,1):
                        if x+xdistance > 7 or x+xdistance <0:
                            continue
                        if xdistance == -1 or xdistance == 1:
                            if board[y-1 ,x+xdistance] == player:
                                continue
                        else:
                            if board[y-1 ,x+xdistance] != 0:
                                continue
                        start = [y, x]
                        end = [y-1, x + xdistance]
                        # moves.append([start, end])
                        moves.append([start[0], start[1], end[0], end[1]])
    return moves

def dorandomlegalmove2(figurepositions, player):
    possiblemoves = getnextstates2(figurepositions, player)
    return possiblemoves[randint(0, len(possiblemoves)) - 1]

def nnstate2board(state):
    b = copy(state)
    b[b == -1] = 2
    return b

def numnextsates(boards, player):
    n = [0] * len(boards)
    for i,b in enumerate(boards):
        n[i] = nummoves(b, player)
    return n

def expandtree(board, player, depth):
    boards = [board]
    for d in xrange(depth):
        nnextstates = numnextsates(boards, player)
        newboards = array([zeros((8,8))] * sum(nnextstates))
        for i,group in enumerate(nnextstates):
            newboards[sum(nnextstates[0:i]): sum(nnextstates[0:(i+1)])] = getnextstates2(boards[i], player)
        player = other(player)
        boards = newboards
    return boards

def featurevec(board, player):
    enemy = other(player)

    pieces = numpieces2(board, player)
    moves = nummoves2(board, player)
    takes = numtakes2(board, player)
    safe = numsafe2(board, player)
    unsafe = numunsafe2(board, player)

    enemypieces = numpieces2(board, enemy)
    enemymoves = nummoves2(board, enemy)
    enemytakes = numtakes2(board, enemy)
    enemysafe = numsafe2(board, enemy)
    enemyunsafe = numunsafe2(board, enemy)

    f1 = array([pieces, moves, takes, safe, unsafe, enemypieces, enemymoves, enemytakes, enemysafe, enemyunsafe])
    #f2 = [item for sublist in f1 for item in sublist]
    #board = [item for sublist in f2 for item in sublist]
    b = f1.reshape(1,640)[0]
    return b

def nnbestmove(board, player, ai):
    moves = getnextstates2(board, player)
    bscore = nnscore(moves[0], player, ai)
    bmove = moves[0]
    for move in moves:
        #print(move)
        score = nnscore(move, player, ai)
        if score > bscore:
            bscore = score
            bmove = move
    return array([bmove, bscore])

def future(board, player, depth):
    b = (board == player) * player
    for d in xrange(depth):
        fboard = zeros((8,8))
        for i in unique(asarray(b))[1:]:
            c = zeros((8,8))
            c[b == i] = player
            fboard += nummoves2(c, player) * i
        b = fboard
    return b

def future2(board, player, depth):
    p = player
    b = copy(board)
    p1b = (board == player) * 1
    p2b = (board == other(player)) * 1
    mb = zeros((8,8))
    for d in xrange(depth):
        playboard = zeros((8,8))
        if p == 1:
            for i in unique(asarray(p1b))[1:]:
                c = zeros((8,8))
                c[p2b != 0] = other(player)
                c[p1b == i] = player
                playboard += nummoves2(c, player) * i
            p1b = playboard
            mb += p1b
        elif p == 2:
            for i in unique(asarray(p2b))[1:]:
                c = zeros((8,8))
                c[p1b != 0] = player
                c[p2b == i] = other(player)
                playboard += nummoves2(c, other(player)) * i
            p2b = playboard
            mb -= p2b
        else:
            print('unrecognised player in future2')
        p = other(p)
    return mb.reshape(1, 64)[0]

def future3(board, player, depth):
    p = player
    p1b = (board == player) * 1
    p2b = (board == other(player)) * 1
    mb = zeros((8,8))
    for d in xrange(depth):
        playboard = zeros((8,8))
        if p == 1:
            for i in unique(asarray(p1b))[1:]:
                c = zeros((8,8))
                c[p2b != 0] = other(player)
                c[p1b == i] = player
                playboard += nummoves2(c, player) * i
            p1b = playboard
            mb += p1b
        elif p == 2:
            for i in unique(asarray(p2b))[1:]:
                c = zeros((8,8))
                c[p1b != 0] = player
                c[p2b == i] = other(player)
                playboard += nummoves2(c, other(player)) * i
            p2b = playboard
            mb -= p2b
        else:
            print('unrecognised player in future2')
        p = other(p)
    return mb

def future4(board, player, depth):
    turn = other(player)

def fatalitycheck(state, player, bound): # always player 1
    b = zeros((8,8))
    if bound == True:
        b[0:state.shape[0], 0:state.shape[1]] = state
    nextstates = getnextstates2(b, player).tolist()
    nextstates.append(b)
    nextstates = array(nextstates)
    return len(nextstates)

def oraclescore1(board, player, depth):
    if player == 1:
        score = sum(future3(board, player, depth)[0])
    elif player == 2:
        score = sum(future3(board, player, depth)[7])
    return score

def oraclescore2(board, player, depth):
    vec = []
    futureb = future3(board, player, depth)
    if player == 1:
        score = sum(futureb[0])
    elif player == 2:
        score = sum(futureb[7])
    vec.append(score)
    vec.append(msum(futureb))
    if player == 2:
        score = sum(futureb[0])
    elif player == 1:
        score = sum(futureb[7])
    vec.append(score)
    return array(vec)

def oraclescore3(board, player): #deprectated
    score = 0
    d = 0
    while score == 0:
        d += 1
        if player == 1:
            score = sum(future3(board, player, d)[0])
        elif player == 2:
            score = sum(future3(board, player, d)[7])
    # if player == 1:
    #     score = sum(future3(board, player, d+1)[0])
    # elif player == 2:
    #     score = sum(future3(board, player, d+1)[7])
    print -1 * score ** (14 - d), d
    return -1 * score ** (14 - d)

def maxscore(board, ai, alpha, beta, depth, player):
    # finished = iswon2(board) #change
    # if finished != False:
    #     # print(board)
    #     if finished == player:
    #         return 10 ** 10
    #     else:
    #         return -10 ** 10
    if depth == 0:
        return predict3(ai, fastboard(board, player)) # change
        # return -1 * oraclescore1(board, player, 11) # change
        # return dsum(board)
    nextstates = getnnnextstates(board, player)
    m = copy(alpha)
    for b in nextstates:
        # print (b)
        # print('-----------------')
        t = minscore(b, ai, m, beta, depth - 1, player)
        m = max([t, m])
        if m >= beta:
            # print('shiny2')
            # print(m)
            # print(alpha)
            return m
    return m

def minscore(board, ai, alpha, beta, depth, player):
    # finished = iswon2(board)
    # if finished != False:
    #     # print(board)
    #     if finished == player:
    #         return 10 ** 10
    #     else:
    #         return -10 ** 10
    if depth == 0:
        return predict3(ai, fastboard(board, player)) # change
        # return -1 * oraclescore1(board, player, 11) # change
        # return dsum(board)
    # nextstates = getnextstates2(board, other(player))
    nextstates = getnnnextstates(board, other(player))
    m = copy(beta)
    for b in nextstates:
        # print (b)
        # print('-----------------')
        t = maxscore(b, ai, alpha, m, depth - 1, player)
        m = min([t, m])
        if m <= alpha:
            # print('shiny1')
            # print(t)
            # print(m)
            # print(alpha)
            return m
    return m

def Tminscore(board, ai, alpha, beta, depth, player, scores, index):
    # finished = iswon2(board)
    # if finished != False:
    #     # print(board)
    #     if finished == player:
    #         return 10 ** 10
    #     else:
    #         return -10 ** 10
    if depth == 0:
        return predict3(ai, fastboard(board, player)) # change
        # return -1 * oraclescore1(board, player, 11) # change
        # return dsum(board)
    # nextstates = getnextstates2(board, other(player))
    nextstates = getnnnextstates(board, other(player))
    m = copy(beta)
    for b in nextstates:
        # print (b)
        # print('-----------------')
        t = maxscore(b, ai, alpha, m, depth - 1, player)
        m = min([t, m])
        if m <= alpha:
            # print('shiny1')
            # print(t)
            # print(m)
            # print(alpha)
            # return m
            scores[index] = m
    # return m
    scores[index] = m

def badheuristicplayer1(board, player, ai, options):
    opponent = other(player)
    boards = [board]
    for depth in range(options['initialdepth']):
        #for depth in range(1):
        nnextstates = numnextsates(boards, player)
        #newboards = array([zeros((8,8))]*sum(nnextstates))
        numnewboards = (options['numownbranch'] ** (depth+1)) * (options['numenemybranch'] ** depth)
        newboards = array([zeros((8,8))] * numnewboards)
        for i,group in enumerate(nnextstates):
            ans = getnextstates2(boards[i], player) # ans = all next states
            newboards[i * options['numownbranch']: (i+1) * options['numownbranch']] = bestboards(ans, player, ai, options['numownbranch'])
            #for n in range(options['numownbranch']):
            # newboards[i * options['numownbranch'] + n] =  ns[n]
        boards = newboards
        nnextstates = numnextsates(boards, opponent)
        #newboards = array([zeros((8,8))]*sum(nnextstates))
        numnewboards = (options['numownbranch'] ** (depth+1)) * (options['numenemybranch'] ** (depth+1))
        newboards = array([zeros((8,8))] * numnewboards)
        for i,group in enumerate(nnextstates):
            ans = getnextstates2(boards[i], opponent) # ans = all next states
            newboards[i * options['numenemybranch']: (i+1) * options['numenemybranch']] = bestboards(ans, opponent, ai, options['numenemybranch'])
            #for n in range(options['numenemybranch']):
            #  newboards[i * options['numenemybranch'] + n] =  ns[n]
        boards = newboards
    return len(boards)

def heuristicplayer2(board, player, ai, options):
    originalplayer = player
    opponent = other(player)
    numoptions = nummoves(board, player)
    moveoptions = getnextstates(board, player)
    boards = [board]
    for depth in range(options['initialdepth']):
        nnextstates = numnextsates(boards, player)
        newboards = array([zeros((8,8))] * sum(nnextstates))
        for i,group in enumerate(nnextstates):
            newboards[sum(nnextstates[0:i]): sum(nnextstates[0:(i+1)])] = getnextstates(boards[i], player)
        player = other(player)
        boards = newboards
        if depth == 0:
            choices = newboards
    lenboards = len(boards)
    bscores = [0] * lenboards
    #boards = boards.astype(int)
    print('hello world 1')
    print(lenboards)
    for bindex, b in enumerate(boards):
        bscores[bindex] = score(b, player, ai)
    bestboardindex = argmin(bscores)
    sectionsize = lenboards / numoptions
    sections = range(0,lenboards+1,sectionsize)
    for i in xrange(numoptions):
        if bestboardindex in range(sections[i],sections[i+1]):
            return choices[i]

def MCS(board, player, options):
    originalplayer = player
    opponent = other(player)
    numoptions = nummoves(board, player)
    moveoptions = getnextstates2(board, player)
    boards = [board]
    rms = []
    for depth in xrange(options['initialdepth']):
        nnextstates = numnextsates(boards, player)
        newboards = array([zeros((8,8))] * sum(nnextstates))
        for i,group in enumerate(nnextstates):
            newboards[sum(nnextstates[0:i]): sum(nnextstates[0:(i+1)])] = getnextstates2(boards[i], player)
        player = other(player)
        boards = newboards
    lenboards = len(boards)
    bscores = [0] * lenboards
    boards = boards.astype(int)
    for bindex, board in enumerate(boards):
        print('doing board ' + str(bindex + 1) + ' of ' + str(lenboards))
        scoresum = 0
        for dc in xrange(options['numdepthcharges']):
            testboard = board
            won = iswon(testboard)
            counter = 0
            while won == False:
                testboard = dorandomlegalmove2(testboard, originalplayer)
                won = iswon(testboard)
                counter += 1
            rms.append(counter)
            print 'its took %d turns' % counter
            scoresum += (won == originalplayer) * 100
        scoresum = scoresum / options['numdepthcharges']
        bscores[bindex] = scoresum
    bestboardindex = argmin(bscores)
    sectionsize = lenboards / numoptions
    sections = range(0,lenboards+1,sectionsize)
    print('=============')
    print(mean(array(rms) + 2))
    for i in xrange(numoptions):
        if bestboardindex in range(sections[i],sections[i+1]):
            return moveoptions[i]

def simpleheuristicplayer(board, player, ai, save = False):
    nextstates = getnextstates2(board, player)
    scores = []
    for bindex, b in enumerate(nextstates):
        contenderscore = score(b, player, ai)
        scores.append(contenderscore)
        if contenderscore == max(scores):
            bestmove = nextstates[bindex]
    if save:
        writefigurepositions('currentgame', bestmove)
    return bestmove

def nnplayer(board, player, ai, s, bsave = False):
    ai = ai2theta(ai, s)
    #nextstates = getnextstates2(subjectiveboard(board, player), player)
    nextstates = getnextstates2(board, player)
    originals = nextstates
    for i in xrange(len(nextstates)):
        nextstates[i] = subjectiveboard(nextstates[i], player)
    bestscore = predict2(ai, nextstates[0].reshape(1,64)[0])
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, nextstates[b].reshape(1,64)[0])
        if s > bestscore:
            bestscore = s
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if player == 1:
        bestboard = turntables(bestboard)
    if bsave:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def nnplayer2(board, player, ai, s, depth, save = False):
    ai = ai2theta(ai, s)
    originalplayer = player
    options = getnextstates2(board, player)
    scores = []
    for b in options:
        player = originalplayer
        nb = [copy(b)]
        for d in xrange(depth):
            # print('------------')
            # print(nb[0])
            # print(player)
            # print(ai)
            nb = nnbestmove(nb[0], player, ai)
            # print(nb[0])
            # print(nb[1])
            if iswon(nb[0]) != False:
                break
            player = other(player)
        scores.append(nb[1])
    if save:
        writefigurepositions('currentgame', options[argmax(scores)])
    return options[argmax(scores)]

def nnplayer3(board, player, ai, s, save = False):
    ai = ai2theta(ai, s)
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, featurevec(nextstates[0], player))
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, featurevec(nextstates[b], player))
        if s > bestscore:
            bestscore = s
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def nnplayer4(board, player, ai, s, save, notuseddepth=1):
    ai = ai2theta(ai, s)
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, nnboard(nextstates[0], player))
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, nnboard(nextstates[b], player))
        if s > bestscore:
            bestscore = s
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def alphabetannplayer(board, player, ai, s, save, depth=1):
    # ai = ai2theta(ai, s)
    nextstates = getnextstates2(board, player)
    scores = [0]*len(nextstates)
    # print(player)
    for bindex, b in enumerate(nextstates):
        # print(b)
        scores[bindex] = minscore(b, ai, -10**11, 10**11, depth, player)
    bb = nextstates[argmax(scores)]
    if save:
        writefigurepositions('currentgame', bb)
    return bb

def fastalphabetannplayer(board, player, ai, s, save, depth=1):
    # ai = ai2theta(ai, s)
    board = nn88board(board)
    nextstates = getnnnextstates(board, player)
    scores = [0]*len(nextstates)
    # print(player)
    for bindex, b in enumerate(nextstates):
        # print(b)
        scores[bindex] = minscore(b, ai, -10**11, 10**11, depth, player)
    bb = nextstates[argmax(scores)]
    if save:
        writefigurepositions('currentgame', normalboard(bb))
    return normalboard(bb)

def Tfastalphabetannplayer(board, player, ai, s, save, depth=1):
    # ai = ai2theta(ai, s)
    board = nn88board(board)
    nextstates = getnnnextstates(board, player)
    scores = [0]*len(nextstates)
    # print(player)
    for bindex, b in enumerate(nextstates):
        # print(b)
        t = threading.Thread(target=Tminscore, args=(b, ai, -10**11, 10**11, depth, player, scores, bindex))
        t.start()
        # Tminscore(b, ai, -10**11, 10**11, depth, player, scores, bindex)
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    bb = nextstates[argmax(scores)]
    if save:
        writefigurepositions('currentgame', normalboard(bb))
    return normalboard(bb)

def nnplayer5(board, player, ai, s, save, depth=1):
    # ai = ai2theta(ai, s)
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, future2(nextstates[0], player, depth))
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, future2(nextstates[b], player, depth))
        if s > bestscore:
            bestscore = s
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def nnplayer6(board, player, ai, s, save, depth = 1):
    # print board
    # ai = ai2theta(ai, s)
    save = False # testing
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, nnboard(nextstates[0], player))#change
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, nnboard(nextstates[b], player))#change
        if s > bestscore:
            bestscore = copy(s)
            bscoreindex = copy(b)
    bestboard = originals[bscoreindex]
    # print(bestscore, player)
    # print bestboard
    # print reshape(nnboard(bestboard, player), (8,8))
    if save:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def oracleplayer1(board, player, save, depth = 12):
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = oraclescore1(nextstates[0], player, depth)
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        score = oraclescore1(nextstates[b], player, depth)
        if score > bestscore:
            bestscore = score
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    print(future3(bestboard, player, depth))
    # print bestscore
    return bestboard

def oracleplayer2(board, player, ai, s, save, depth = 11):
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, oraclescore2(nextstates[0], player, depth))
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        score = predict2(ai, oraclescore2(nextstates[b], player, depth))
        if score > bestscore:
            bestscore = score
            bscoreindex = b
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    # print bestscore
    return bestboard

def oracleplayer3(board, player, save):
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    for d in range(14, -1, -1):
        for b in nextstates:
            if oraclescore1(b, player, d) == 0:
                if save:
                    writefigurepositions('currentgame', b)
                return b

def oracleplayer4(board, player, save):
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    if player == 1:
        for rowskips in range(1, 8):
            bscore = -10 ** 10
            wscore = 10 ** 10
            for bindex in range(len(nextstates)):
                tempb = copy(nextstates[bindex])
                tempb[rowskips:, :][tempb[rowskips:, :] == other(player)] = 0
                # print rowskips
                # print(tempb)
                score = oraclescore1(tempb, player, 14)
                # print score
                if score > bscore:
                    bscore = score
                    bestboardindex = bindex
                if score < wscore:
                    wscore = score
                # print(bscore)
                # print(originals[bestboardindex])
            if wscore != 0:
                return originals[bestboardindex]
    if player == 2:
        for rowskips in range(7, 0, -1):
            bscore = -10 ** 10
            wscore = 10 ** 10
            for bindex in range(len(nextstates)):
                tempb = copy(nextstates[bindex])
                tempb[:rowskips, :][tempb[:rowskips, :] == other(player)] = 0
                # print rowskips
                # print(tempb)
                score = oraclescore1(tempb, player, 14)
                # print score
                if score > bscore:
                    bscore = score
                    bestboardindex = bindex
                if score < wscore:
                    wscore = score
                # print(bscore)
                # print(originals[bestboardindex])
            if wscore != 0:
                return originals[bestboardindex]

def nnplayer7(board, player, ai, s, save, depth = 1):
    save = False # testing
    nextstates = getnextstates2(board, player)
    originals = copy(nextstates)
    bestscore = predict2(ai, nnboard6(nextstates[0], player))#change
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict2(ai, nnboard6(nextstates[b], player))#change
        if s > bestscore:
            bestscore = copy(s)
            bscoreindex = copy(b)
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', bestboard)
    return bestboard

def fastplayer(board, player, ai, s, save = False, depth = 1):
    save = False # testing
    board = nn88board(board)
    nextstates = getnnnextstates(board, player)
    originals = copy(nextstates)
    # if len(nextstates) == 0:
    #     return False
    bestscore = predict3(ai, fastboard(nextstates[0], player))#change
    bscoreindex = 0
    for b in xrange(1,len(nextstates)):
        s = predict3(ai, fastboard(nextstates[b], player))#change
        if s > bestscore:
            bestscore = copy(s)
            bscoreindex = copy(b)
    bestboard = originals[bscoreindex]
    if save:
        writefigurepositions('currentgame', normalboard(bestboard))
    return normalboard(bestboard)

def MCTSplayer(board, player, ai, s, C, save = False, iters = 1000):
    state = UCT.BreakthroughState()
    state.board = nn88board(board)
    state.playerJustMoved = other(player)
    move = UCT.UCT(state, ai, s, C, False, iters)
    mboard = normalboard(makemove4(board, move))
    # print mboard
    return mboard

def main():
    test4 = zeros((8,8))
    test5 = zeros((8,8))
    test6 = zeros((8,8))
    test7 = zeros((8,8))
    teststate1 = zeros((4,3))
    teststate1[0,0] = 1
    teststate1[0,1] = 1
    teststate1[3,0] = 2
    teststate1[3,1] = 2
    test4[0,0] = 1
    test4[7,7] = 2
    test5[4,4] = 1
    test5[5,5] = 2
    test6[4,3] = 1
    test6[6,2] = 1
    test6[5,1] = 1
    test7[1,4] = 1

    nntest = nn88board(test)
    # print(splitlist(range(7), 4))
    print(GetNextMoves(nntest, 1))



if __name__ == "__main__":
    main()


#testai1 = matrix(ones((95,1)))
#simpleheuristicplayer(test, 1, testai1)
#MCS(test, 1, testoptions)
#heuristicplayer(test, 1, testai1, testoptions)
# print(test4)
# start_time = time.time()
# print(getnextstates2(test4, 2))
# print("--- %s seconds ---" % (time.time() - start_time))
#print(test)

# start_time = time.time()
# for i in range(1500):
#   getnextstates2(test, 1)
# print("--- %s seconds ---" % (time.time() - start_time))

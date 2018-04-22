from featurecomputation import *
from Breakthrough import *
from itertools import chain

# an ai is strucured as follows:
# numpy matrix. ai[i] = weight the ai gives the heuristic number i. no player indication means own. no row indication means whole board. # = number of
# [#pieces #moves #takes #safe1 #safe2 #unsafe #piecesenemy #movesenemy #takesenemy #safe1enemy #safe2enemy #unsafeenemy]
# for each item in the array above there are also 2 variables c_featurebyrow and a_featurebyrow .: c_movesbyrow, a_movesbyrow.
# all these are used in the heuristic score calculation as follows:
# score = ai[0] * numpieces + ai[1] * nummoves etc... + c_movesbyrow * a_movesbyrow**(row) etc...

def makemove2(board, origin, destination):
  temp = copy(board)
  figure = temp[origin[1],origin[0]]
  temp[destination[1],destination[0]] = board[origin[1],origin[0]]
  temp[origin[1],origin[0]] = 0.
  return temp


def score(board, player, ai):
  score = 0.0
  staticvars = matrix(zeros((1, 12)))
  staticvars[0,0:6] = array([numpieces(board, player), nummoves(board, player), numtakes(board, player), numsafe(board, player, 1), numsafe(board, player, 2), numunsafe(board, player)])
  player = other(player)
  staticvars[0,6:12] = array([numpieces(board, player), nummoves(board, player), numtakes(board, player), numsafe(board, player, 1), numsafe(board, player, 2), numunsafe(board, player)])
  score += staticvars * ai[0:12]

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
  return float(score + sum(scalingvars))

def bestboards(boards, player, ai, num):
  scores = [0] * len(boards)
  best = array([[zeros((8,8))]*num])
  for index, board in enumerate(boards):
    scores[index] = score(board, player, ai)
  for i in range(num):
    mini = argmin(scores)
    best[0,i] = boards[mini]
    scores = delete(scores, mini)
  return best

def getnextstates(board, player):
  board = copy(board).astype(int)
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


def numnextsates(boards, player):
  n = [0] * len(boards)
  for i,b in enumerate(boards):
    n[i] = nummoves(b, player)
  return n

def heuristicplayer(board, player, ai, options):
  opponent = other(player)
  boards = [board]
  #for depth in range(options['initialdepth']):
  for depth in range(1):
    nnextstates = numnextsates(boards, player)
    newboards = array([[zeros((8,8))]*sum(nnextstates)])
    print(newboards)
    for i,group in enumerate(nnextstates):
      print([sum(nnextstates[0:i]): sum(nnextstates[0:i]) + group, 0])
      newboards[sum(nnextstates[0:i]): sum(nnextstates[0:i]) + group, 0] =  getnextstates(boards[i], player)
    boards = newboards
    print(boards)
    print(newboards)
    nnextstates = numnextsates(boards, opponent)
    newboards = array([[zeros((8,8))]*sum(nnextstates)])
    for i,group in enumerate(nnextstates):
      newboards[sum(nnextstates[0:i]): sum(nnextstates[0:i]) + group, 0] =  getnextstates(boards[i], opponent)
    boards = newboards
  return len(boards)


testoptions = {'numownbranch' : 3, 'numenemybranch' : 3, 'initialdepth' : 5, 'numdepthcharges' : 5}
testai1 = matrix(ones((36,1)))
score(test2, 1, testai1)
dorandomlegalmove(test.astype(int), 1)
test[1,0]
emptySign
bestboards([test, test, test], 1, testai1, 1)
makemove2(test, [3, 1], [3, 2])
test

getnextstates(test, 1)[0,0:10]
dictlegalmovesbyplayer(test.astype(int), 1)
heuristicplayer(test, 1, testai1, testoptions)
numnextsates([test, test], 1)
array([[zeros((8,8))]*2])


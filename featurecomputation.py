from numpy import *
import time

def other(player):
  if player == 1:
    return 2
  elif player == 2:
    return 1
  else:
    print("player not recognised in other()")

def numpieces(board, player, row = 'all'):
  row = relativerow(board, player, row)
  if row == 'all':
    return sum(sum(board == player))
  else:
    return sum(sum(board[row] == player))

def numpieces2(board, player):
  return (board == player) * 1

def relativerow(board, player, row):
  bsize = int(sqrt(size(board)))
  if row == 'all':
    return 'all'
  elif player == 2:
    return bsize - (1 + row)
  return row

def nummoves(board, player, row = 'all'): # when row = 7 always returns 0
  row = relativerow(board, player, row)
  bsize = int(sqrt(size(board)))
  moves  = 0
  essentialboard = (board == player) * 1
  enemyessentialboard = (board == other(player) * 1)
  #essentialboard[essentialboard == 0] = 2
  forewardmoves = zeros((bsize, bsize))
  forewardrightmoves = zeros((bsize, bsize))
  forewardleftmoves = zeros((bsize, bsize))
  if player == 1: # player 1 moves down board
    forewardmoves[1:bsize] = essentialboard[1:bsize] + essentialboard[0:bsize-1]
    forewardrightmoves[1:bsize, 1:bsize] = essentialboard[1:bsize, 1:bsize] + essentialboard[0:bsize-1, 0:bsize-1]
    forewardleftmoves[1:bsize, 0:bsize-1] = essentialboard[1:bsize, 0:bsize-1] + essentialboard[0:bsize-1, 1:bsize]
  elif player == 2: # player 2 moves up board
    forewardmoves[0:bsize-1] = essentialboard[0:bsize-1] + essentialboard[1:bsize]
    forewardrightmoves[0:bsize-1, 1:bsize] = essentialboard[0:bsize-1, 1:bsize] + essentialboard[1:bsize, 0:bsize-1]
    forewardleftmoves[0:bsize-1, 0:bsize-1] = essentialboard[0:bsize-1, 0:bsize-1] + essentialboard[1:bsize, 1:bsize]
  else:
     print("player not recognised")
  forewardleftmoves[forewardleftmoves == 2] = 0
  forewardrightmoves[forewardrightmoves == 2] = 0
  forewardmoves[forewardmoves == 2] = 0
  forewardleftmoves -= essentialboard
  forewardrightmoves -= essentialboard
  forewardmoves -= (essentialboard + enemyessentialboard)
  if row == 'all':
    moves = sum(sum(forewardleftmoves == 1)) + sum(sum(forewardrightmoves == 1)) + sum(sum(forewardmoves == 1))
  else:
    moves = sum(forewardleftmoves[row] == 1) + sum(forewardrightmoves[row] == 1) + sum(forewardmoves[row] == 1)
  return moves

def nummoves2(board, player): # when row = 7 always returns 0
  bsize = int(sqrt(size(board)))
  moves  = 0
  essentialboard = (board == player) * 1
  enemyessentialboard = (board == other(player) * 1)
  #essentialboard[essentialboard == 0] = 2
  forewardmoves = zeros((bsize, bsize))
  forewardrightmoves = zeros((bsize, bsize))
  forewardleftmoves = zeros((bsize, bsize))
  if player == 1: # player 1 moves down board
    forewardmoves[1:bsize] = essentialboard[1:bsize] + essentialboard[0:bsize-1]
    forewardrightmoves[1:bsize, 1:bsize] = essentialboard[1:bsize, 1:bsize] + essentialboard[0:bsize-1, 0:bsize-1]
    forewardleftmoves[1:bsize, 0:bsize-1] = essentialboard[1:bsize, 0:bsize-1] + essentialboard[0:bsize-1, 1:bsize]
  elif player == 2: # player 2 moves up board
    forewardmoves[0:bsize-1] = essentialboard[0:bsize-1] + essentialboard[1:bsize]
    forewardrightmoves[0:bsize-1, 1:bsize] = essentialboard[0:bsize-1, 1:bsize] + essentialboard[1:bsize, 0:bsize-1]
    forewardleftmoves[0:bsize-1, 0:bsize-1] = essentialboard[0:bsize-1, 0:bsize-1] + essentialboard[1:bsize, 1:bsize]
  else:
     print("player not recognised")
  forewardleftmoves[forewardleftmoves == 2] = 0
  forewardrightmoves[forewardrightmoves == 2] = 0
  forewardmoves[forewardmoves == 2] = 0
  forewardleftmoves -= essentialboard
  forewardrightmoves -= essentialboard
  forewardmoves -= (essentialboard + enemyessentialboard)
  moves = (forewardleftmoves == 1)*1 + (forewardrightmoves == 1)*1 + (forewardmoves == 1)*1
  return moves

def numtakes(board, player, row = 'all'):
  row = relativerow(board, player, row)
  bsize = int(sqrt(size(board)))
  takes = 0
  essentialboard = (board == player) * 1
  enemyessentialboard = (board == other(player)) * 2
  forewardrightmoves = zeros((bsize, bsize))
  forewardleftmoves = zeros((bsize, bsize))
  if player == 1: # player 1 moves down board
    forewardrightmoves[1:bsize, 1:bsize] = essentialboard[0:bsize-1, 0:bsize-1] + enemyessentialboard[1:bsize, 1:bsize]
    forewardleftmoves[1:bsize, 0:bsize-1] = essentialboard[0:bsize-1, 1:bsize] + enemyessentialboard[1:bsize, 0:bsize-1]
  elif player == 2: # player 2 moves up board
    forewardrightmoves[0:bsize-1, 1:bsize] = essentialboard[1:bsize, 0:bsize-1] + enemyessentialboard[0:bsize-1, 1:bsize]
    forewardleftmoves[0:bsize-1, 0:bsize-1] = essentialboard[1:bsize, 1:bsize] + enemyessentialboard[0:bsize-1, 0:bsize-1]
  else:
    print("player not recognised")
  if row == 'all':
    takes = sum(sum(forewardleftmoves == 3)) + sum(sum(forewardrightmoves == 3))
  else:
    takes = sum(forewardleftmoves[row] == 3) + sum(forewardrightmoves[row] == 3)
  return takes

def numtakes2(board, player):
  bsize = int(sqrt(size(board)))
  takes = 0
  essentialboard = (board == player) * 1
  enemyessentialboard = (board == other(player)) * 2
  forewardrightmoves = zeros((bsize, bsize))
  forewardleftmoves = zeros((bsize, bsize))
  if player == 1: # player 1 moves down board
    forewardrightmoves[1:bsize, 1:bsize] = essentialboard[0:bsize-1, 0:bsize-1] + enemyessentialboard[1:bsize, 1:bsize]
    forewardleftmoves[1:bsize, 0:bsize-1] = essentialboard[0:bsize-1, 1:bsize] + enemyessentialboard[1:bsize, 0:bsize-1]
  elif player == 2: # player 2 moves up board
    forewardrightmoves[0:bsize-1, 1:bsize] = essentialboard[1:bsize, 0:bsize-1] + enemyessentialboard[0:bsize-1, 1:bsize]
    forewardleftmoves[0:bsize-1, 0:bsize-1] = essentialboard[1:bsize, 1:bsize] + enemyessentialboard[0:bsize-1, 0:bsize-1]
  else:
    print("player not recognised")
  takes = (forewardleftmoves == 3)*1 + (forewardrightmoves == 3)*1
  return takes

def numsafe(board, player, degree, row = 'all'):
  row = relativerow(board, player, row)
  if row == 'all':
    nsafe = sum(sum(safemap(board, player) == degree))
  else:
    nsafe = sum(sum(safemap(board, player)[row] == degree))
  return nsafe

def numsafe2(board, player):
  return safemap(board, player)

def numsafedegree1(board, player, row = 'all'):
  return numsafe(board, player, 1, row)

def numsafedegree2(board, player, row = 'all'):
  return numsafe(board, player, 2, row)

def safemap(board, player):
  bsize = int(sqrt(size(board)))
  essentialboard = (board == player) * 1
  forewardrightmoves = zeros((bsize, bsize))
  forewardleftmoves = zeros((bsize, bsize))
  nsafe = 0
  smap = zeros((bsize, bsize))
  if player == 1: # player 1 moves down board
    forewardrightmoves[1:bsize, 1:bsize] = essentialboard[0:bsize-1, 0:bsize-1] + essentialboard[1:bsize, 1:bsize]
    forewardleftmoves[1:bsize, 0:bsize-1] = essentialboard[0:bsize-1, 1:bsize] + essentialboard[1:bsize, 0:bsize-1]
  elif player == 2: # player 2 moves up board
    forewardrightmoves[0:bsize-1, 1:bsize] = essentialboard[1:bsize, 0:bsize-1] + essentialboard[0:bsize-1, 1:bsize]
    forewardleftmoves[0:bsize-1, 0:bsize-1] = essentialboard[1:bsize, 1:bsize] + essentialboard[0:bsize-1, 0:bsize-1]
  else:
    print("player not recognised")
  s1 = zeros((bsize, bsize))
  s2 = zeros((bsize, bsize))
  s1[forewardrightmoves == 2] = 1
  s2[forewardleftmoves == 2] = 1
  smap = s1 + s2
  return smap

def numunsafe(board, player, row = 'all'):
  row = relativerow(board, player, row)
  if row == 'all':
    nunsafe = numpieces(board, player) - sum(sum(safemap(board, player) != 0))
  else:
    nunsafe = numpieces(board, player, row) - sum(safemap(board, player)[row] != 0)
  return nunsafe

def numunsafe2(board, player):
  essentialboard = (board == player) * 1
  return (((numsafe2(board, player) == 0)*1) == essentialboard)*1

test = zeros((8,8))
test[(0,1),:] = 1
test[(6,7),:] = 2
test
test2 = zeros((8,8))
test2[4,(2,4,6)] = 1
test2[5, 3:6] = 2
test2
test3 = copy(test2)
test3[3,(1,3,5)] = 1
test3
test4 = zeros((8,8))
test4[0, 1] = 1
test4[1, 0] = 2
test4

#print(numpieces2(test, 2))
# print(test4)
# print('')
# print(numunsafe2(test4, 2))

#print(nummoves2(test4, 2))
#numpieces(test, 1)
#nummoves(test3, 2, 3) # 22
#numtakes(test3, 1, 5)
#numsafe(test3, 1, 2)
#safemap(test3, 1)
#numunsafe(test3, 2, 5)


from __future__ import print_function
from gamemanager import *
from featurecomputation import *
from Breakthrough import *
from mutator import *
from math import log
from random import choice
import pickle
import operator


def writeais(ais, fname = 'ais'):
    f = open(fname, 'wb')
    sPickle.s_dump(ais, f)
    #f.close()

def writeais2(ais, fname = 'ais'):
    f = open(fname, 'wb')
    pickle.dump(ais, f)
    #f.close()

def readais(fname = 'ais'):
    f = open(fname)
    ais = sPickle.s_load(f)
    #f.close()
    return list(ais)

def seedai(ailength):
  return matrix((random.rand(ailength, 1) - 0.5) / 2.5)

def seedais(numais, ailength):
  ais = []
  for i in xrange(numais):
    ais.append(seedai(ailength))
  return ais

def game(ai1, ai2, ngames = 2):
    initialboard = zeros((8,8))
    initialboard[(0,1),:] = 1
    initialboard[(6,7),:] = 2
    board = copy(initialboard)
    won = False
    save = True
    # s = [64, 300, 300, 300, 300, 1]
    # s = [64, 160, 80, 1]
    # s = [640, 400, 400, 1]
    # s = [640, 700, 500, 300, 200, 1]
    # s = [64, 64, 64, 64, 64, 64, 1]
    # s = [64, 64, 64, 64, 1]
    # s = [64, 128, 64, 1]
    # s = [64, 64, 128, 1]
    # s = [64, 32, 32, 1]
    s = [64, 40, 20, 1]
    ai1 = ai2theta2(ai1, s)
    ai2 = ai2theta2(ai2, s)
    depth = 11
    playerfunc = fastplayer
    if ngames == 1:
        starter = choice([1,2])
        if starter == 1:
            while won == False:
                board = playerfunc(board, 1, ai1, s, save, depth)
                won = iswon(board)
                if won != False:
                    return won
                board = playerfunc(board, 2, ai2, s, save, depth)
                won = iswon(board)
                if won != False:
                    return won
        else:
            while won == False:
                board = playerfunc(board, 2, ai2, s, save, depth)
                won = iswon(board)
                if won != False:
                    return won
                board = playerfunc(board, 1, ai1, s, save, depth)
                won = iswon(board)
                if won != False:
                    return won
    elif ngames == 2:
        g1, g2 = 0, 0
        while won == False:
            board = playerfunc(board, 2, ai1, s, save, depth)
            won = iswon(board)
            if won == 2:
                g1 = 1
                break
            board = playerfunc(board, 1, ai2, s, save, depth)
            won = iswon(board)
            if won == 1:
                g1 = 2
        won = False
        board = copy(initialboard)
        while won == False:
            board = playerfunc(board, 2, ai2, s, save, depth)
            won = iswon(board)
            if won == 2:
                g2 = 2
                break
            board = playerfunc(board, 1, ai1, s, save, depth)
            won = iswon(board)
            if won == 1:
                g2 = 1
        winner = 0
        if g1 == g2:
            winner = g1
        return winner

def freeforalltournament(ais, verbose = False): # uses outdated game func
    wins = [0] * len(ais)
    played = {}
    for i in range(len(ais)):
        played[i] = []
    for ai1index,ai1 in enumerate(ais):
        for ai2index,ai2 in enumerate(ais):
            if ai1index in played[ai2index]:
                continue
                # pass
            if ai1index != ai2index:
                # played[ai1index].append(ai2index)
                played[ai2index].append(ai1index)
                if verbose:
                    print ('ai'+str(ai1index)+' playing against ai'+str(ai2index))
                outcome = game(ai1, ai2)
                if outcome == 1:
                    wins[ai1index] += 1
                    if verbose: print ('ai'+str(ai1index)+' won')
                else:
                    wins[ai2index] += 1
    return (array(wins)**2.5).astype(int).tolist()
    # return wins

def laddertournament(ais): # uses outdated game func
  numparticipants = len(ais)
  wins = [0] * numparticipants
  numstages = int(log(numparticipants, 2))
  stagesizes = [0] * numstages
  stage = ais
  #results = [0] * (numstages+1)
  results = []
  for i in range(numstages):
    stagesizes[i] = numparticipants / 2 ** i
  for index,i in enumerate(stagesizes):
    print('round '+str(index + 1))
    nextstage = []
    for matches in range(0,i,2):
      ai1 = stage[matches]
      ai2 = stage[matches+1]
      print ('ai'+str(matches)+' playing against ai'+str(matches+1))
      outcome = game(ai1, ai2)
      if outcome == 1:
        results.append(stage[matches])
        nextstage.append(matches)
      else:
        results.append(stage[matches+1])
        nextstage.append(matches+1)
    stage = []
    for n in nextstage:
      #results.append(ais[n])
      stage.append(ais[n])
  for winner in results:
    aiindex = 0
    for ai in ais:
      if makelist(ai) == makelist(winner):
        wins[aiindex] += 1
      aiindex += 1
  return (array(wins)+1).tolist()

def one_v_x_tournament(ais, x = 5):
    numplayermodi = 1
    wins = array([0] * len(ais))
    for ai1index, ai1 in enumerate(ais):
        print ('ai'+str(ai1index)+"'s time to shine!", end = '\r')
        enemypool = list(delete(range(len(ais)), ai1index))
        opponents = [0] * x
        for i in range(x):
            selection = random.choice(enemypool)
            enemypool.remove(selection)
            opponents[i] = selection
        for opponentindex in opponents:
            gameresult = game(ai1, ais[opponentindex])
            #finboard = readfigurepositions('currentgame')
            if gameresult == 1:
                wins[ai1index] += 1 #+ numplayermodi * (numpieces(finboard, 1) - numpieces(finboard, 2))
                wins[opponentindex] -= 2 #+ numplayermodi * (numpieces(finboard, 1) - numpieces(finboard, 2))
            elif gameresult == 2:
                wins[opponentindex] += 1 #+ numplayermodi * (numpieces(finboard, 2) - numpieces(finboard, 1))
                wins[ai1index] -= 2 #+ numplayermodi * (numpieces(finboard, 2) - numpieces(finboard, 1))
    #wins = multiply(wins, 2).tolist()
    wins += abs(min(wins)) +1
    wins = wins ** 2.5
    wins = wins.astype(int)
    #return abs(array(wins)).tolist()
    return wins.tolist()

def makelist(ai):
  return transpose(ai).tolist()[0]

def addchampiontoHOF(champ):
    HOF = readais('hall of fame')
    HOF.append(champ)
    writeais(HOF, 'hall of fame')

def evolve(numais, seed, hof, s, ailen, playername):
    # s = [640, 400, 400, 1]
    # s = [64, 160, 80, 1]
    # s = [64, 64, 64, 64, 64, 64, 1]
    # s = [640, 700, 500, 300, 200, 1]
    # s = [64, 64, 64, 1]
    # s = [64, 64, 64, 64, 1]
    # s = [64, 128, 64, 1]
    # ailen = 16835
    # net = buildNetwork(64, 32, 32, 1, outclass=LinearLayer)
    tcounter = array([1,1])
    gameplayer = fastplayer
    if seed:
        writeais(tcounter, 'tcounter')
        writeais(ones((numais, 2)) * 0.025, 'mutate_strats')
        writeais([seedai(ailen)], 'hall of fame')
        writeais(seedais(numais, ailen))
    ais = readais()
    counter = 1
    HOF = readais('hall of fame')
    # for j in range(10):
    while True:
        i = readais('tcounter')[0]
        print ('--------------------------')
        print('Tournament number '+str(counter) + ' | '+str(readais('tcounter')[0]))
        results = array(one_v_x_tournament(ais, 6))
        # results = array(freeforalltournament(ais))
        print('Tournament results: '+str(results.tolist()))
        if hof:
            newchamp = ais[argmax(results)]
            addchampiontoHOF(newchamp)
            HOF = readais('hall of fame')
        ais = nextgen(ais, results, 0.25, s, HOF, gameplayer)
        # ais = orgynew(ais, results)
        means = reshape(mean(ais, 1), (1, numais))
        means = mean(means)
        print('ai means: '+str(means))
        writeais(ais)
        writeais(array(readais('tcounter'))+1, 'tcounter')
        if i % 100 == 0:
            r = freeforalltournament(ais)
            writeais(ais[argmax(r)], 'current best')
            writeais(ais, playername + str(i))
            if i >= 200:
                check_progression(playername, [i -100])
        counter += 1

def war(f1name = 'f1', f2name = 'f2'): # don't know what this function is good for
    faction1 = readais(f1name)
    faction2 = readais(f2name)
    f1wins = 0
    f2wins = 0
    draws = 0
    print('starting war...')
    for f1ai in faction1:
        for f2ai in faction2:
            gresult = game(f1ai, f2ai, 2)
            if gresult == 1:
                f1wins += 1
            elif gresult == 2:
                f2wins += 1
            else:
                draws += 1
    print('war results:')
    print(f1name+' won '+str(f1wins)+' battles')
    print(f2name+' won '+str(f2wins)+' battles')
    print('there were '+str(draws)+' draws')
    print('but in the end it was good for absolutley nothing!')
    print('============================')
    return [f1wins, f2wins, draws]

def check_progression(prefix, num):
    print('############################################')
    for n in num:
        name1 = prefix+str(n)
        name2 = prefix+str(n+100)
        print(name1+' VS '+name2)
        war(name1, name2)
    print('all wars completed')
    print('############################################')

def check_generation(prefix, gennum):
    outcomes = {}
    for n in range(gennum, 0, -100)[1:]:
        r = war(prefix+str(gennum), prefix+str(n))
        outcomes[n] = r[0] - r[1]
    sortedoutcomes = sorted(outcomes.items(), key=operator.itemgetter(1))
    print (sortedoutcomes)
    return sortedoutcomes

def worldwar(prefix, involved):
    outcomes =  {}
    for n in involved:
        outcomes[n] = 0
    for n1 in involved:
        outcomes[n1] = 0
        for n2 in involved:
            if n1 == n2:
                continue
            wresult = war(prefix+str(n1), prefix+str(n2))
            outcomes[n1] += wresult[0]
            outcomes[n1] -= wresult[1]
            outcomes[n2] += wresult[1]
            outcomes[n2] -= wresult[0]
    sortedoutcomes = sorted(outcomes.items(), key=operator.itemgetter(1))
    print (sortedoutcomes)
    return array(sortedoutcomes)

def main():
    # 3547
    # d = 14
    # check_generation('fastplayer', 3600)
    # worldwar('fastplayer', range(2700, 3701, 100))
    # check_progression('fastplayer', range(0, 1300, 100)[1:])
    # writeais(array([2701, 1]), 'tcounter')

    # r = worldwar('fastplayer', range(100, 3601, 100))
    # bestprefixes = r[[range(16)], 0][0]
    # bestprefixes =array([2900, 1500, 1600, 3000, 3100, 2800, 3200, 1800, 2700, 3300, 300, 1200, 1100, 1700,  200, 1300])
    # ais = []
    # for i in range(16):
    #     print('Starting tournament '+str(i+1)+'...')
    #     a = readais('fastplayer'+str(bestprefixes[i]))
    #     t = freeforalltournament(a)
    #     print('results: '+str(t))
    #     ais.append(a[argmax(t)])
    #     print('_____________________________________')
    # writeais(array(ais), 'ais')

    evolve(16, True, False, [64, 40, 20, 1], 3441, playername = 'fastplayer')


    # # war()
    # writeais(ones((16, 2)) * 0.025 , 'mutate_strats')
    # writeais(array([1301,0]), 'tcounter')
if __name__ == "__main__":
    main()

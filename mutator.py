from __future__ import print_function
from random import randint, random
from bisect import bisect
from numpy import matrix, zeros, random, sqrt, array, exp, linalg, copy, delete, argmin, concatenate, arctan, pi, \
    multiply, divide, power, reshape
from numpy.random import randn
from numpy.random import standard_cauchy
import greatjourney
import NeuralNetwork
import warnings
import featurecomputation
import gamemanager
import sys
# import multiprocessing as mp

import time
# import struct

# def floatToBits(f):
#   s = struct.pack('>f', f)
#   return struct.unpack('>l', s)[0]
#
# def bitsToFloat(b):
#   s = struct.pack('>l', b)
#   return struct.unpack('>f', s)[0]

def choicediversity(ai1, ai2):
    pass

def cauchy(x, t = 1):
    f1 = random.random((x.shape[0], 1)) - 0.5
    f2 = power(random.random((x.shape[0], 1)), 2)
    return x + t * ((1/pi) * divide(f1, (f2 + power(x, 2))))

def eucldist(coords1, coords2):
    """ Calculates the euclidean distance between 2 lists of coordinates. """
    return linalg.norm(coords1 - coords2)

def decision(probability):
    return random.random() < probability

def piechartselection(fitnessscores):
    if sum(fitnessscores) < 2:
        print('not enough non zero fitnessscores')
        fitnessscores = [1] * len(fitnessscores)
    wholechart = float(sum(fitnessscores))
    numsubjects = len(fitnessscores)
    P = [0] * numsubjects
    for subjectindex, subjectscore in enumerate(fitnessscores):
        P[subjectindex] =  subjectscore / wholechart
    cdf = [P[0]]
    for i in xrange(1, len(P)):
        cdf.append(cdf[-1] + P[i])
    random_ind1 = bisect(cdf, random.random())
    random_ind2 = random_ind1
    while random_ind2 == random_ind1:
        random_ind2 = bisect(cdf, random.random())
    return [random_ind1, random_ind2]
    # return bisect(cdf, random.random())

def mutateold(ai, mutationrate):
  # mutationstep = 0.1
  # for genomeindex, genome in enumerate(ai):
  #   bucket = [[True],[False] * int(((1 / mutationrate) - 1))]
  #   bucket = [item for sublist in bucket for item in sublist]
  #   if choice(bucket):
  #     updown = choice([-1, 1])
  #     ai[genomeindex] += updown * mutationstep

  if decision(mutationrate):
    ai = ai + ((random.rand(len(ai),1) - 0.5) / 0.05)
  return ai

def mutate(ai, mutationrate):
  # mutationstep = 0.1
  # for genomeindex, genome in enumerate(ai):
  #   bucket = [[True],[False] * int(((1 / mutationrate) - 1))]
  #   bucket = [item for sublist in bucket for item in sublist]
  #   if choice(bucket):
  #     updown = choice([-1, 1])
  #     ai[genomeindex] += updown * mutationstep

  if decision(mutationrate):
    ai = ai + ((random.rand(len(ai),1) - 0.5) / 0.05)
  return ai

def createchild(parent):
    chromosomelen = len(parent)
    T = 1 / sqrt(2 * sqrt(chromosomelen))
    child = multiply(parent, exp(T * (random.random((chromosomelen, 1)) - 0.5)))
    return child
    # child = parent + ((random.random((chromosomelen, 1)) - 0.5) / 2.5)

def createchild2(parent, notusedstrats):
    chromosomelen = len(parent)
    T = 1 / sqrt(2 * sqrt(chromosomelen))
    child = multiply(parent, exp(T * (random.random((chromosomelen, 1)) - 0.5)))
    # child = parent + ((random.random((chromosomelen, 1)) - 0.5) / 2.5)
    return [child , 0]

def createchild3(parent1, parent2):
    pass

def AMMOchild(parent, strats):
    chromosomelen = len(parent)
    T = 1 / sqrt(2 * chromosomelen)
    Tp = 1 / sqrt(2 * sqrt(chromosomelen))
    nstrats = strats * exp(T * randn(2) + Tp * randn(2))
    nchild = parent + nstrats[0] * (standard_cauchy((chromosomelen, 1)) + nstrats[1] * random.normal(chromosomelen, 1))
    return [nchild, nstrats]

def createchildold(parent1, parent2, mutationrate):
  chromosomelen = len(parent1)
  parent1 = mutate(parent1, mutationrate)
  parent2 = mutate(parent2, mutationrate)
  cutoff = randint(0,chromosomelen)
  child = matrix(zeros((chromosomelen, 1)))
  # for p1gen in range(0,cutoff):
  #   child[p1gen] =  float(parent1[p1gen])
  # for p2gen in range(cutoff,chromosomelen):
  #   child[p2gen] =  float(parent2[p2gen])
  child[0:cutoff] = parent1[0:cutoff]
  child[cutoff:chromosomelen] = parent2[cutoff:chromosomelen]
  #child = [parent1[0:cutoff], parent2[cutoff:chromosomelen]]
  #child = [item for sublist in child for item in sublist]
  return child

def randomboards(numboards):
    boards = []
    for i in range(numboards):
        b = zeros((8,8))
        ran = random.randint(6,16)
        b[(random.random(ran)*7).astype(int), (random.random(ran)*8).astype(int)] = 1
        ran = random.randint(6,16)
        b[(random.random(ran)*7).astype(int)+1, (random.random(ran)*8).astype(int)] = 2
        boards.append(b)
    return boards

def CD(c, P):
    mincd = eucldist(c, P[0])
    for i in xrange(1, len(P)-1):
        mincd = min([mincd, eucldist(c, P[i])])
    return mincd

def CD2(c, P, player, s, numboards):
    complete = False
    while complete == False:
        complete = True
        try:
            boards = randomboards(numboards)
            min_diversity = numboards
            for pop in P:
                diversity = numboards
                for b in boards:
                    if reshape(player(b, 1, NeuralNetwork.ai2theta2(c, s), s, False), (1,64))[0].tolist() == reshape(player(
                            b, 1,
                            NeuralNetwork.ai2theta2(pop, s), s, False), (1,64))[0].tolist():
                        diversity -= 1
                        min_diversity = min([min_diversity, diversity])
        except IndexError:
            complete = False
            warnings.warn('IndexError occured in CD2!')
    return min_diversity

def challengeHOF(challenger, HOF, reqwinpercentage = 0.5):
    if len(HOF) < 5:
        return True
    numdefenders = len(HOF) / 5
    #numdefenders = 50
    defenders = [0] * numdefenders
    enemies = range(len(HOF))
    for i in xrange(numdefenders):
        selection = random.choice(enemies)
        enemies.remove(selection)
        defenders[i] = selection
    challwins = 0
    gamecount = 0
    for champindex in defenders:
        if greatjourney.game(challenger, HOF[champindex]) == 1:
            challwins += 1
        gamecount += 1
        if challwins >= reqwinpercentage * numdefenders:
            return True
        if challwins + (numdefenders - gamecount) < int(reqwinpercentage * numdefenders):
            return False
    return False

def challengenrandomHOFs(challenger, HOF, n):
    if len(HOF) < n:
        print('bot enough HOFs')
        return True
    numdefenders = n
    defenders = [0] * numdefenders
    enemies = range(len(HOF))
    for i in xrange(numdefenders):
        selection = random.choice(enemies)
        enemies.remove(selection)
        defenders[i] = selection
    for champindex in defenders:
        if greatjourney.game(challenger, HOF[champindex]) == 2:
            return False
    return True

def challengelastnHOFs(challenger, HOF, n = 3):
    if len(HOF) < n:
        numdefenders = len(HOF)
    else:
        numdefenders = n
    for i in xrange(1, numdefenders+1):
        if greatjourney.game(challenger, HOF[-i], 2) != 1:
            return False
    return True

def nextgen(ais, aiscores, mutationrate, s, HOF, gameplayer):
    numdbs = 150
    checkHOF = False
    ngen = copy(ais)
    F1 = copy(ais)
    tobekept = []
    parenttries = 0
    while len(tobekept) < 1:
        tobekept = []
        parenttries += 1
        parentsindexes = piechartselection(aiscores)
        parent = copy(ais[parentsindexes[0]])
        allmstrats = greatjourney.readais('mutate_strats')
        mstrats = allmstrats[parentsindexes[0]]
        newinf = AMMOchild(parent, mstrats) # change
        # newinf = createchild2(parent, mstrats) # change
        child = newinf[0]
        nmstrats = newinf[1]
        HOFtries = 0
        if checkHOF:
            while challengeHOF(child, HOF) == False:
                HOFtries += 1
                print('child ' +str(HOFtries)+' did not win against enough HOFs...', end='\r')
                parentsindexes = piechartselection(aiscores)
                parent = ais[parentsindexes[0]]
                newinf = AMMOchild(parent, mstrats) # change
                # newinf = createchild2(parent, mstrats) # change
                child = newinf[0]
                nmstrats = newinf[1]
            print('child '+str(HOFtries+1)+' won enough of his games against the HOF!')
        # allmstrats[parentsindexes[0]] = nmstrats
        # greatjourney.writeais(allmstrats, 'mutate_strats')
        tobedeleted = []
        inferioraiindexes = []
        for aiindex, ai in enumerate(ais):
            if greatjourney.game(child, ai, 2) == 1: # changed ngames to 1
                tobekept.append(aiindex)
                inferioraiindexes.append(aiindex)
            else:
                tobedeleted.append(aiindex) # unused
        if len(tobekept) == 0:
            print('child '+str(parenttries)+' was without victory', end='\r')
            # tobekept.append(argmin(aiscores)) # testing
            # inferioraiindexes.append(argmin(aiscores)) # testing
    print('child '+str(parenttries)+', son of ai'+str(parentsindexes[0])+', won '+str(len(tobekept))+' games against '
                                                                                                   'following elders: '
                                                                                 ''+str(
        tobekept))
    # greatjourney.writeais(allmstrats, 'mutate_strats')
    F1 = array(F1)[tobekept]
    if len(tobekept) != 0:
        CDs = [0] * len(F1)
        for i in xrange(len(F1)):
            testset = [0] * (len(ais) - 1)
            if tobekept[i] == 0:
                testset = ais[1:]
            else:
                testset[:tobekept[i] - 1] = ais[:tobekept[i]]
                testset[tobekept[i] - 1:] = ais[tobekept[i] + 1:]
            # CDs[i] = CD(F1[i], testset)
            CDs[i] = CD2(F1[i], testset, gameplayer, s, numdbs)
            del testset
        print('contribution to diversity scores: '+str(CDs))
        # print('tempdebug1: '+str(inferioraiindexes[argmin(CDs)]))
        testset = [0] * (len(ais) - 1)
        i = tobekept[argmin(CDs)]
        # print('====================')
        # print(len(testset))
        # print(inferioraiindexes[argmin(CDs)])
        # print(len(ais[:inferioraiindexes[argmin(CDs)]]))
        # print(len(CDs))
        testset[:i - 1] = ais[:inferioraiindexes[argmin(CDs)]]
        testset[i - 1:] = ais[inferioraiindexes[argmin(CDs)]+1:]
        minCD = min(CDs)
        # cdchild = CD(child, testset)
        cdchild = CD2(child, testset, gameplayer, s, numdbs)
        print('child CD score: '+str(cdchild))
        if cdchild > minCD:
            print('diversified!')
            replacable = []
            for memindex, mem in enumerate(CDs):
                if mem == minCD:
                    replacable.append(memindex)
            replacable = array(array(inferioraiindexes)[array(replacable)])
            worst = replacable[argmin(aiscores[replacable])]
            ngen[worst] = child
            allmstrats[worst] = nmstrats
            # ngen[inferioraiindexes[argmin(CDs)]] = child
            # allmstrats[inferioraiindexes[argmin(CDs)]] = nmstrats
        else:
            print('not diversified!')
            # smallestscore = min(aiscores)
            # replacable = []
            # for memindex, mem in enumerate(aiscores):
            #     if mem == smallestscore:
            #         replacable.append(memindex)
            # replacable = array(replacable)
            # worst = replacable[argmin(CDs[replacable])]
            # ngen[worst] = child
            # allmstrats[worst] = nmstrats
            ngen[argmin(aiscores)] = child
            allmstrats[argmin(aiscores)] = nmstrats
    else:
        print('child won against none of the parents')
        # ngen[argmin(aiscores)] = child
    print('childs mtation strats: '+str(nmstrats))
    greatjourney.writeais(allmstrats, 'mutate_strats')
    return ngen

def Tnextgen(ais, aiscores, mutationrate, s, HOF, gameplayer):
    numdbs = 150
    checkHOF = False
    ngen = copy(ais)
    F1 = copy(ais)
    tobekept = []
    parenttries = 0
    while len(tobekept) < 1:
        tobekept = []
        parenttries += 1
        parentsindexes = piechartselection(aiscores)
        parent = copy(ais[parentsindexes[0]])
        allmstrats = greatjourney.readais('mutate_strats')
        mstrats = allmstrats[parentsindexes[0]]
        newinf = AMMOchild(parent, mstrats) # change
        # newinf = createchild2(parent, mstrats) # change
        child = newinf[0]
        nmstrats = newinf[1]
        HOFtries = 0
        if checkHOF:
            while challengeHOF(child, HOF) == False:
                HOFtries += 1
                print('child ' +str(HOFtries)+' did not win against enough HOFs...', end='\r')
                parentsindexes = piechartselection(aiscores)
                parent = ais[parentsindexes[0]]
                newinf = AMMOchild(parent, mstrats) # change
                # newinf = createchild2(parent, mstrats) # change
                child = newinf[0]
                nmstrats = newinf[1]
            print('child '+str(HOFtries+1)+' won enough of his games against the HOF!')
        # allmstrats[parentsindexes[0]] = nmstrats
        # greatjourney.writeais(allmstrats, 'mutate_strats')
        tobedeleted = []
        inferioraiindexes = []
        for aiindex, ai in enumerate(ais):
            if greatjourney.game(child, ai, 2) == 1: # changed ngames to 1
                tobekept.append(aiindex)
                inferioraiindexes.append(aiindex)
            else:
                tobedeleted.append(aiindex) # unused
        if len(tobekept) == 0:
            print('child '+str(parenttries)+' was without victory', end='\r')
            # tobekept.append(argmin(aiscores)) # testing
            # inferioraiindexes.append(argmin(aiscores)) # testing
    print('child '+str(parenttries)+', son of ai'+str(parentsindexes[0])+', won '+str(len(tobekept))+' games against '
                                                                                                   'following elders: '
                                                                                 ''+str(
        tobekept))
    # greatjourney.writeais(allmstrats, 'mutate_strats')

    F1 = array(F1)[tobekept]
    if len(tobekept) != 0:
        CDs = [0] * len(F1)
        for i in xrange(len(F1)):
            testset = [0] * (len(ais) - 1)
            if tobekept[i] == 0:
                testset = ais[1:]
            else:
                testset[:tobekept[i] - 1] = ais[:tobekept[i]]
                testset[tobekept[i] - 1:] = ais[tobekept[i] + 1:]
            # CDs[i] = CD(F1[i], testset)
            CDs[i] = CD2(F1[i], testset, gameplayer, s, numdbs)
            del testset
        print('contribution to diversity scores: '+str(CDs))
        # print('tempdebug1: '+str(inferioraiindexes[argmin(CDs)]))
        testset = [0] * (len(ais) - 1)
        i = tobekept[argmin(CDs)]
        # print('====================')
        # print(len(testset))
        # print(inferioraiindexes[argmin(CDs)])
        # print(len(ais[:inferioraiindexes[argmin(CDs)]]))
        # print(len(CDs))
        testset[:i - 1] = ais[:inferioraiindexes[argmin(CDs)]]
        testset[i - 1:] = ais[inferioraiindexes[argmin(CDs)]+1:]
        minCD = min(CDs)
        # print(minCD)
        # time.sleep(2)
        # cdchild = CD(child, testset)
        cdchild = CD2(child, testset, gameplayer, s, numdbs)
        print('child CD score: '+str(cdchild))
        if cdchild >= minCD:
            print('diversified!')
            replacable = []
            for memindex, mem in enumerate(CDs):
                if mem == minCD:
                    replacable.append(memindex)
            replacable = array(array(inferioraiindexes)[array(replacable)])
            worst = replacable[argmin(aiscores[replacable])]
            ngen[worst] = child
            allmstrats[worst] = nmstrats
            # ngen[inferioraiindexes[argmin(CDs)]] = child
            # allmstrats[inferioraiindexes[argmin(CDs)]] = nmstrats
        else:
            print('not diversified!')
            # smallestscore = min(aiscores)
            # replacable = []
            # for memindex, mem in enumerate(aiscores):
            #     if mem == smallestscore:
            #         replacable.append(memindex)
            # replacable = array(replacable)
            # worst = replacable[argmin(CDs[replacable])]
            # ngen[worst] = child
            # allmstrats[worst] = nmstrats
            ngen[argmin(aiscores)] = child
            allmstrats[argmin(aiscores)] = nmstrats
    else:
        print('child won against none of the parents')
        # ngen[argmin(aiscores)] = child
    print('childs mtation strats: '+str(nmstrats))
    greatjourney.writeais(allmstrats, 'mutate_strats')
    return ngen

def orgyold(ais, aiscores, mutationrate, requiredchildren):
  children = []
  #parentgent = 0
  #childgent = 0
  while len(children) < requiredchildren:
    #start_time = time.time()
    parent1 = ais[piechartselection(aiscores)]
    parent2 = ais[piechartselection(aiscores)]
    #parentgent += (time.time() - start_time)
    #start_time = time.time()
    child = createchild(parent1, parent2,  mutationrate)
    #childgent += (time.time() - start_time)
    children.append(child[0])
    children.append(child[1])
  #print(parentgent)
  #print(childgent)
  return children

def orgynew(ais, aiscores):
  children = []
  while len(children) < len(aiscores):
    parentindex = piechartselection(aiscores)[0]
    parent = ais[parentindex]
    allmstrats = greatjourney.readais('mutate_strats')
    mstrats = allmstrats[parentindex]
    newinf = AMMOchild(parent, mstrats)
    child = newinf[0]
    nmstrats = newinf[1]
    allmstrats[parentindex] = nmstrats
    children.append(child)
    greatjourney.writeais(allmstrats, 'mutate_strats')
  return children

def testpiechartselection():
  counter = [0]*3
  for i in xrange(1000):
    counter[piechartselection([2, 4, 8])] += 1
  return counter

def main():
    # print(randomboards(1))
    # print(createchild(matrix('[1;2]')))
    # c = createchild(matrix('[1;2;3;4]'), matrix('[0;1;2;3]'),1)
    # print(c[0])
    # print(c[1])
    # print(CD(matrix('[1;2;3;4]'), [matrix('[1.01;2;3;4.01]'), matrix('[1;2;4;5]')]))
    #print(createchild(matrix('1;2;3;4;5'), matrix('5;4;3;2;1'), 0.01))
    #testpiechartselection()
    #orgy([[1,2,3,4,5],[5,4,3,2,1],[100,100,100,100,100]], [0,20,5], 0.1, 3)
    #print(mutate(matrix('1;2;3;4;5'), 1))
    bs = randomboards(1)
    ai = greatjourney.readais('current best')
    s = [64, 40, 20, 1]
    for i, b in enumerate(bs):
        # if i % 100 == 0:
        #     print(i, end='\r')
        print(i, end='\r')
        b = greatjourney.nn88board(b)
        o1 = greatjourney.fastalphabetannplayer(b, 1, ai, s, False, 2)
        o2 = greatjourney.fastalphabetannplayer(b, 2, ai, s, False, 2)
        n1 = greatjourney.Tfastalphabetannplayer(b, 1, ai, s, False, 2)
        n2 = greatjourney.Tfastalphabetannplayer(b, 2, ai, s, False, 2)
        print((reshape(o1, (1,64))[0]).tolist() == (reshape(n1, (1,64))[0]).tolist())
        print((reshape(o2, (1,64))[0]).tolist() == (reshape(n2, (1,64))[0]).tolist())
        # if len(o1) != len(n1) or len(o2) != len(n2):
        #     print('error')
        #     print(b)
        #     print(len(o1))
        #     print(len(n1))
        #     print(len(o2))
        #     print(len(n2))
        #     break




if __name__ == "__main__":
    main()
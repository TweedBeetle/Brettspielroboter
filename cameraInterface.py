from math import sqrt
import os
import shutil
import pickle
from PIL import Image
import numpy as np

def eucldist(coords1, coords2):
    """ Calculates the euclidean distance between 2 lists of coordinates. """
    return np.linalg.norm(coords1 - coords2)

def distance2(a, b):
    return sum(sum(abs(a-b)))

def getWebcamSnapshot(webcamNum, snapshotName):

    from VideoCapture import Device

    cam = Device(webcamNum)
    cam.saveSnapshot(snapshotName)

def getChunksAndData(imageName, numChunks):
    ''' req Image , sqrt , os, shutil
    cuts up image m into numChunks grayscale pieces and puts them in a subdir of the
    execution dir. Then creates data dir and creates numChunks data.txt files
    which can be used in an octave ML algorithm
    '''

    m = Image.open(imageName)
    homedir = os.getcwd()
    chunkdir = homedir + '\Chunks'
    filedir = homedir + '\data'
    if os.path.isdir(filedir):
        shutil.rmtree(filedir)
    if os.path.isdir(chunkdir):
        shutil.rmtree(chunkdir)
    os.mkdir("Chunks")
    os.mkdir("data")
    os.chdir(chunkdir)
    r = int(sqrt(numChunks))
    width = m.size[0] / r
    height = m.size[1] / r
    n = 1
    for i in range(1, r + 1):
        for o in range(1, r + 1):
            box = ((o - 1) * width, (i - 1) * height, o * width, i * height)
            # print(box)
            region = m.crop(box)
            # region.show()
            # region = region.convert('L')
            region.save("Chunk" + str(n) + ".png")
            n += 1
    for i in range(1, numChunks + 1):
        os.chdir(chunkdir)
        chunk = Image.open('Chunk' + str(i) + '.png')
        os.chdir(filedir)
        data = open('Data' + str(i) + '.txt', 'wb')
        datalist = list(chunk.getdata())

        # sPickle.s_dump(datalist, data)
        pickle.dump(datalist, data)
        # for i in datalist:                  # <-------- enable for simple text encoding
        #     data.write(str(i)+'\n')

        #print(len((list(chunk.getdata()))))
        data.close()
    os.chdir(homedir)

def makeSquare(imageName):
    m = Image.open(imageName)
    height = m.size[1]
    width = m.size[0]
    edge = (width - height) / 2
    box = (edge,0, width - edge,height)
    m = m.crop(box)
    m.save(imageName)

def reRez(imageName, size):
    m = Image.open(imageName)
    m2 = m.resize(size)
    m2.save(imageName)

def readBoard():
    snapshotName = 'board.jpg'
    boardSize = 8*8
    chunkSize = (20, 20)

    numChunks = sqrt(boardSize)
    snapshotSize = (int(chunkSize[0] * numChunks), int(chunkSize[1] * numChunks))

    getWebcamSnapshot(0, snapshotName)
    # print('hello world 1')
    makeSquare(snapshotName)
    # print('hello world 2')
    reRez(snapshotName, snapshotSize)
    # print('hello world 3')
    makeSquare(snapshotName)
    # print('hello world 4')
    getChunksAndData(snapshotName, boardSize)

def calib():
    readBoard()
    homedir = os.getcwd()
    filedir = homedir + '\data'
    # os.chdir(filedir)
    for i in range(1,4):
        name = '\Data'+str(i)+'.txt'
        shutil.copy(filedir+name, homedir+name)
    print('calibration complete!')

def idenBoard():

    distancefunk = eucldist

    homedir = os.getcwd()
    filedir = homedir + '\data'

    f = open('Data1.txt')
    emptyfield = list(pickle.load(f))
    f.close()

    f = open('Data2.txt')
    player1field = list(pickle.load(f))
    f.close()

    f = open('Data3.txt')
    player2field = list(pickle.load(f))
    f.close()

    # print emptyfield
    # print player1field
    # print player2field

    emptyfield = np.array([np.array(item) for item in emptyfield])
    player1field = np.array([np.array(item) for item in player1field])
    player2field = np.array([np.array(item) for item in player2field])

    b = np.zeros((8,8))
    os.chdir(filedir)

    # print emptyfield
    # print player1field
    # print player2field

    for y in range(8):
        for x in range(8):
            n = y * 8 + x + 1
            f = open('Data'+str(n)+'.txt')
            field = list(pickle.load(f))
            f.close()
            field  = np.array([np.array(item) for item in field])

            # print field

            diffempty = distancefunk(field, emptyfield)
            diffplayer1 = distancefunk(field, player1field)
            diffplayer2 = distancefunk(field, player2field)

            guess = np.argmin([diffempty, diffplayer1, diffplayer2])

            # print diffempty
            # print diffplayer1
            # print diffplayer2
            # print '______________________________'

            b[y,x] = guess

    b = np.flipud(np.fliplr(b))

    print(b)
    return b

if __name__ == "__main__":
    calib()
    # readBoard()
    # idenBoard()

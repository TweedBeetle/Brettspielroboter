from __future__ import print_function
import serial
import time
import numpy as np
import gamemanager as gm

s = serial.Serial("COM7",9600)
lastpos = (0, 0, 0, 0, 0)

def uArmMessage(armRot, armStr, armHt, handAng, ctlData):
    msg =[0xFF,0xAA,((armRot>>8)& 0xFF),
          (armRot&0xFF),((armStr>>8)&0xFF),
          (armStr&0xFF),((armHt>>8)&0xFF),
          (armHt&0xFF),((handAng>>8)&0xFF),
          (handAng&0xFF),(1 if ctlData else 2)];
    return msg

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(int(rho), int(np.rad2deg(phi)))

def pol2cart(rho, phi):
    phi = np.deg2rad(phi)
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def moveMade(b1, b2, player): # returns [[startx, starty], [endx, endy]]
    change = b1 != b2
    # print(change)
    start = []
    if player == 1:
        yrange = range(8)
    else:
        yrange = reversed(range(8))
    for y in yrange:
        for x in range(8):
            if change[y,x] == True:
                if start == []:
                    start = [y, x]
                else:
                    end = [y, x]
                    return [start, end]

def reenact(b1, b2, player):
    m = moveMade(b1, b2, player)
    if b1[m[1][0], m[1][1]] != 0:
        takePiece(m[1])
    movePiece(m)

def pickUp(field):
    moveAbove(field)
    new = lastpos
    new[2] = lastpos[2] - 9
    new[1] = new[1] + 3
    new[4] = 1
    moveTo(new, 1) # move down and suck
    new[2] = new[2] + 20
    new[1] = new[1] - 20
    moveTo(new, 1)
    # print('picked')

def putDown(field):
    # print(lastpos)
    new = lastpos
    new[0] = field[0]
    new[1] = field[1]
    # print(fieldCoords(new))
    # print('0')
    moveTo(fieldCoords(new), 8)
    # print('1')
    new[2] = new[2] -  23
    # time.sleep(2)
    # print(fieldCoords(new))
    moveTo(fieldCoords(new), 5)
    new[4] = 0
    moveTo(fieldCoords(new), 3)
    new[2] = new[2] + 23
    moveTo(fieldCoords(new), 3)
    moveTo([0, 0, 0, 0, 0], 10)

def pickUpandPlace(fields):
    start = fields[0]
    end = fields[1]
    moveAbove(start)
    new = lastpos
    new[2] = lastpos[2] - 5
    new[4] = 1
    moveTo(new, 1) # move down and suck
    new[2] = new[2] + 20
    moveTo(new, 5)

    new = lastpos
    new[0] = end[0]
    new[1] = end[1]
    print(fieldCoords(new))
    moveTo(fieldCoords(new), 5)
    new[2] = new[2] = -20
    moveTo(fieldCoords(new), 1)
    new[4] = 0
    moveTo(fieldCoords(new), 3)
    new[2] = new[2] + 5
    moveTo(fieldCoords(new), 1)
    moveOrder([0, 0, 0, 0, 0], 1)

def movePiece(fields):
    start = fields[0]
    end = fields[1]
    pickUp(start)
    putDown(end)

def takePiece(field):
    pickUp(field)
    moveTo([50, 100, -10, 0, 1], 8)
    moveTo([50, 100, -10, 0, 0], 1)

def moveAbove(field, speed = 8):
    row = field[0]
    if row == 0:
        h = -32
    elif row == 1:
        h = -33
    elif row == 2:
        h = -35
    elif row == 3:
        h = -37
    elif row == 4:
        h = -37
    elif row == 5:
        h = -38
    elif row == 6:
        h = -41
    elif row == 7:
        h = -42
    pos = [field[0], field[1], h, 0, 0]
    moveTo(fieldCoords(pos), speed)

def fieldCoords(pos):
    row = pos[0]
    col = pos[1]
    if row == 0:
        if col == 0:
            r = 39
            s = 30
        elif col == 1:
            r = 31
            s = 16
        elif col == 2:
            r = 22
            s = 8
        elif col == 3:
            r = 13
            s = 4
        elif col == 4:
            r = 3
            s = 3
        elif col == 5:
            r = -7
            s = 7
        elif col == 6:
            r = -16
            s = 18
        elif col == 7:
            r = -24
            s = 34
    elif row == 1:
        if col == 0:
            r = 35
            s = 51
        elif col == 1:
            r = 28
            s = 42
        elif col == 2:
            r = 21
            s = 33
        elif col == 3:
            r = 12
            s = 30
        elif col == 4:
            r = 4
            s = 30
        elif col == 5:
            r = -5
            s = 34
        elif col == 6:
            r = -13
            s = 42
        elif col == 7:
            r = -20
            s = 55
    elif row == 2:
        if col == 0:
            r = 32
            s = 72
        elif col == 1:
            r = 26
            s = 63
        elif col == 2:
            r = 19
            s = 57
        elif col == 3:
            r = 12
            s = 55
        elif col == 4:
            r = 4
            s = 54
        elif col == 5:
            r = -4
            s = 57
        elif col == 6:
            r = -11
            s = 64
        elif col == 7:
            r = -18
            s = 74
    elif row == 3:
        if col == 0:
            r = 29
            s = 95
        elif col == 1:
            r = 24
            s = 87
        elif col == 2:
            r = 18
            s = 80
        elif col == 3:
            r = 12
            s = 77
        elif col == 4:
            r = 4
            s = 77
        elif col == 5:
            r = -2
            s = 82
        elif col == 6:
            r = -9
            s = 87
        elif col == 7:
            r = -15
            s = 96
    elif row == 4:
        if col == 0:
            r = 28
            s = 116
        elif col == 1:
            r = 23
            s = 110
        elif col == 2:
            r = 17
            s = 107
        elif col == 3:
            r = 11
            s = 104
        elif col == 4:
            r = 5
            s = 104
        elif col == 5:
            r = -2
            s = 105
        elif col == 6:
            r = -8
            s = 110
        elif col == 7:
            r = -12
            s = 116
    elif row == 5:
        if col == 0:
            r = 26
            s = 142
        elif col == 1:
            r = 22
            s = 133
        elif col == 2:
            r = 17
            s = 130
        elif col == 3:
            r = 12
            s = 128
        elif col == 4:
            r = 5
            s = 127
        elif col == 5:
            r = 0
            s = 129
        elif col == 6:
            r = -5
            s = 133
        elif col == 7:
            r = -10
            s = 138
    elif row == 6:
        if col == 0:
            r = 25
            s = 165
        elif col == 1:
            r = 20
            s = 160
        elif col == 2:
            r = 16
            s = 152
        elif col == 3:
            r = 11
            s = 151
        elif col == 4:
            r = 6
            s = 151
        elif col == 5:
            r = 1
            s = 151
        elif col == 6:
            r = -4
            s = 156
        elif col == 7:
            r = -9
            s = 164
    elif row == 7:
        if col == 0:
            r = 23
            s = 189
        elif col == 1:
            r = 20
            s = 182
        elif col == 2:
            r = 15
            s = 178
        elif col == 3:
            r = 11
            s = 177
        elif col == 4:
            r = 6
            s = 177
        elif col == 5:
            r = 2
            s = 177
        elif col == 6:
            r = -4
            s = 180
        elif col == 7:
            r = -8
            s = 187

    return [r, s, pos[2], pos[3], pos[4]]

def moveTo(pos, speed):
    opos = lastpos #originalpos
    sleeptime = 1.0 / speed
    # polarpos = cart2pol(pos[1], pos[0])
    # pos[1] = polarpos[0]
    # pos[0] = polarpos[1]
    # print(pos)
    diff =  np.array(pos) - np.array(lastpos)
    biggestdiff = max(abs(diff))
    # print diff
    moves = []

    for movenum in range(1,biggestdiff+1, speed):
        newmove = [0] * 5
        for i in range(5):
            newmove[i] = int(opos[i] + movenum * (diff[i] / float(biggestdiff)))
        moves.append(newmove)
    for m in moves:
        # pass
        moveOrder(m, 0.03)
        # print(m)
        # time.sleep(0.1)
    moveOrder(pos, 1)
    # time.sleep(1)

def moveOrder(position, waittime = 0.1):
    global lastpos
    lastpos = position
    # msg = uArmMessage(position[0], position[1], position[2], position[3], position[4])
    msg = uArmMessage(position[0], position[1], position[2], position[0] * -1, position[4])
    n = 0
    timeout = time.time() + waittime
    while True:
        s.write("".join(map(chr,msg)))
        n += 1
        if time.time() > timeout:
            # print(n, end='\r')
            break
    s.write("".join(map(chr,msg)))

def reset():
    moveOrder((0, 0, 0, 0, 0), 1)
    # time.sleep(3)

def main():
    # time.sleep(1)

    reset()
    movePiece([[1,7],[1,7]])
    # takePiece([3,4])
    # pickUp([7,5])

    time.sleep(1)
    # reset()

    # for r in range(5,7):
    #     for c in range(8):
    #         movePiece([[r,c],[r+1, c]])

    # moveAbove([5,5])

    # test1 = np.zeros((8,8))
    # test2 = np.zeros((8,8))
    # test1[4,4] = 1
    # test1[5,5] = 2
    # test2[4,4] = 2
    # print(test1)
    # print(test2)
    #
    # reenact(test1, test2, 2)
    reset()



if __name__ == "__main__":
    main()
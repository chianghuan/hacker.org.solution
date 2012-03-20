#!/usr/bin/python27

import urllib
import time
import re

problemUrl = 'http://www.hacker.org/runaway/index.php'
username = ''
password = ''

def initAcc():
    f = open('account.pass', 'r')
    global username, password
    username = f.readline().strip()
    password = f.readline().strip()
    f.close()


def mkurl(sol=None):
    if sol != None:
        sol = '&path=' + sol
    else:
        sol = ''
    return problemUrl + '?name=' + username + \
            '&password=' + password + sol

def nextLevel(sol):
    levelUrlString = mkurl(sol)
    levelUrl = urllib.urlopen(levelUrlString)
    pageText = levelUrl.read() 
    seobj = re.search(r'"FVterrainString.*?"', pageText)
    if seobj == None:
        # not a valid game
        if re.search(r'sucked', pageText) != None:
            # wrong answer
            print pageText
            return None
        # exception on page content
        fileobj = open('exception.html', 'w')
        fileobj.write(pageText)
        print 'Error page have been written into exception.html'
        return None
    # resolve the arguments of the game
    args = seobj.group().strip('"').split('&')
    terrain = ''
    fmax = fmin = boardx = boardy = level = 0
    for arg in args:
        aname, aval = arg.split('=')
        if aname == 'FVterrainString':
            terrain = aval
        elif aname == 'FVinsMax':
            fmax = int(aval)
        elif aname == 'FVinsMin':
            fmin = int(aval)
        elif aname == 'FVboardX':
            boardx = int(aval)
        elif aname == 'FVboardY':
            boardy = int(aval)
        elif aname == 'FVlevel':
            level = int(aval)
    return terrain, fmax, fmin, boardx, boardy, level

def fold(terrain, xs, ys, bx, by):
    mapret = [[0 for i in range(ys + 1)] for j in range(xs + 1)]
    stx, sty = 0, 0
    while True:
        if stx >= bx or sty >= by:
            break
        for i in range(xs + 1):
            if stx + i >= bx:
                break
            for j in range(ys + 1):
                if sty + j >= by:
                    break
                if mapret[i][j] != 1 and terrain[stx + i + (sty + j) * bx] == 'X':
                    mapret[i][j] = 1
        stx = stx + xs
        sty = sty + ys
    return mapret

def dfsSSSP(mapmatrix, mark, sx, sy, xs, ys):
    res = ''
    if sx == xs and sy == ys:
        return res
    if sx > xs or sy > ys:
        return None
    if mark[sx][sy] == 1:
        return None
    mark[sx][sy] = 1
    if sx < xs and mapmatrix[sx + 1][sy] == 0:
        ret = dfsSSSP(mapmatrix, mark, sx + 1, sy, xs, ys)
        if ret != None:
            return 'R' + ret
    if sy < ys and mapmatrix[sx][sy + 1] == 0:
        ret = dfsSSSP(mapmatrix, mark, sx, sy + 1, xs, ys)
        if ret != None:
            return 'D' + ret
    return None

def foldAndSSSPSolve(terrain, fmax, fmin, bx, by, level):
    print 'solving level', level, '  fmin fmax =', fmin, fmax
    for r in range(fmin, fmax + 1):
        for xs in range(0, r):
            ys = r - xs
            if xs >= bx:
                xs = bx
            if ys >= by:
                ys = by
            mapmatrix = fold(terrain, xs, ys, bx, by)
            mark = [[0 for i in range(ys + 1)] for j in range(xs + 1)]
            res = dfsSSSP(mapmatrix, mark, 0, 0, xs, ys)
            if res != None:
                return res
    return None

if __name__ == "__main__" :
    initAcc()
    lastSol = None
    while True:
        t1 = time.time()
        retvar = nextLevel(lastSol)
        t2 = time.time()
        if retvar == None:
            break;
        print 'retrived time(seconds):', t2 - t1
        lastSol = foldAndSSSPSolve(*retvar)
        if lastSol == None:
            print 'no solution found!'
            break
        t3 = time.time()
        print 'solved:', lastSol
        print 'time(seconds):', t3 - t2
    print 'Program terminated'

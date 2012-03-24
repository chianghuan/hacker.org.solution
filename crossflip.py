#!/usr/bin/python27 -u

import subprocess
import urllib2
import httplib
import random
import urllib
import base64
import time
import math
import os
import re

problemUrl = 'http://www.hacker.org/cross/index.php'
username = ''
password = ''

def initAcc():
    f = open('account.pass', 'r')
    global username, password
    username = f.readline().strip()
    password = f.readline().strip()
    f.close()

def dump(tmat):
    n = len(tmat)
    for x in tmat:
        print bin(x[0]).lstrip('-0b').rjust(n,'0'), x[1]

def gauss(mat, tar):
    n = len(mat)
    print 'coeffi matrix sz:', n
    t1 = time.time()
    tmat = [[x, 0] for i, x in enumerate(mat)]
    maskarr = [1L<<i for i in range(n)]
    for i in range(n):
        tmat[i][1] = tar[i]
    for k in range(n):
        for i in range(k, n):
            if tmat[i][0] & maskarr[n-k-1] != 0L:
                tmp = tmat[i]
                tmat[i] = tmat[k]
                tmat[k] = tmp
                break
        for i in range(k+1, n):
            if tmat[i][0] & maskarr[n-k-1] == 0L:
                continue
            tmat[i][0] ^= tmat[k][0]
            tmat[i][1] ^= tmat[k][1]
    t2 = time.time()
    print 'time for delta:', t2 - t1
    # elim from down to up
    for k in range(n-1, -1, -1):
        mask = maskarr[n - k - 1]
        for i in range(k-1,-1,-1):
            if (tmat[i][0] & mask) == 0:
                continue
            tmat[i][0] ^= tmat[k][0]
            tmat[i][1] ^= tmat[k][1]
    res = 0L
    t1 = time.time()
    print 'time for elim:', t1 - t2
    for i in range(n):
        while True:
            if tmat[i][0] != 0 and tmat[i][0] & (tmat[i][0]-1) != 0:
                tmat[i][0] &= tmat[i][0] - 1
            else:
                break
    for i in range(n):
        if tmat[i][1] == 1:
            res |= (tmat[i][0]) 
    print 'time for result:', time.time() - t1
    return bin(res).lstrip('-0b').rjust(n, '0')

def solve(board, level):
    print 'solving level:', level
    h = len(board)
    w = len(board[0])
    print 'level size:', h, w
    t1 = time.time()
    block = []
    for i in range(h*w):
        if board[i/w][i%w] == '2':
            block += [i]
    proj = [0 for i in range(h*w)] # board -> mat
    projb = [0 for i in range(h*w-len(block))] # mat -> board
    num = 0
    for i in range(h*w):
        if board[i/w][i%w] != '2':
            proj[i] = num
            projb[num] = i
            num += 1
    mat = [0L for i in range(h*w-len(block))]
    tar = [0 for i in range(h*w-len(block))]
    for i in range(h*w):
        if board[i/w][i%w] == '1':
            tar[proj[i]] = 1
    # build mat
    for i in range(h*w):
        x = i/w
        y = i%w
        if board[x][y] == '2':
            continue
        # 4 directions
        for j in range(x, h):
            if board[j][y] == '2':
                break
            setmat(mat, proj[i], proj[j*w+y])
        for j in range(x-1, -1, -1):
            if board[j][y] == '2':
                break
            setmat(mat, proj[i], proj[j*w+y])
        for j in range(y, w):
            if board[x][j] == '2':
                break
            setmat(mat, proj[i], proj[x*w+j])
        for j in range(y-1, -1, -1):
            if board[x][j] == '2':
                break
            setmat(mat, proj[i], proj[x*w+j])
    # gauss
    t2 = time.time()
    print 'preprocess time:', t2 - t1
    res = gauss(mat, tar)
    print 'gauss time:', time.time() - t2
    resarr = ['0' for i in range(h*w)]
    # should be inserting 0 into block positions
    # putting the return value into rite pos' instead is fine
    for i in range(len(res)):
        resarr[projb[i]] = res[i]
    res = ''
    for s in resarr:
        res += s
    sol = 'lvl=' + level + '&sol='  + res
    return sol

def setmat(mat, x, y):
    n = len(mat)
    mat[x] |= (1L << n-y-1)

def nextLevel(sol):
    # post the request
    req = urllib2.Request(problemUrl)
    reqdata = 'name=' + username + '&password=' + password
    if sol != None:
        reqdata = reqdata + '&' + sol
    req.add_data(reqdata)
    levelUrl = urllib2.urlopen(req)
    # get content
    pageText = levelUrl.read()
    seobj = re.search(r'boardinit = ".*?"', pageText)
    if seobj == None:
        print pageText
        return None
    args = seobj.group()[12:].strip('"').split(',')
    seobj = re.search(r'var level = .*?;', pageText)
    level = ''
    if seobj != None:
        level = seobj.group()[12:-1]
    return args, level

if __name__ == "__main__":
    lastSol = None
    initAcc()
    while True:
        print
        t1 = time.time()
        retvar = None
        retvar = nextLevel(lastSol)
        t2 = time.time()
        if retvar == None:
            break
        print 'retrived time(seconds):', t2 - t1
        lastSol = solve(*retvar)
        # print 'solved:', lastSol
        t3 = time.time()
        print 'solved. time total(seconds):', t3 - t2
    print 'Program terminated'

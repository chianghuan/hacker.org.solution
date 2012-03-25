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

def solve(board, level):
    print 'solving level:', level
    h = len(board)
    w = len(board[0])
    
    fi = open('crossinput.txt', 'w')
    fi.write('%d\n' % h)
    for x in board:
        fi.write(x)
        fi.write('\n')
    fi.close()

    proc = subprocess.Popen('crossflip.exe 1')
    while True:
        time.sleep(1)
        if proc.poll() != None:
            break

    # read rusult from crossoutput.txt
    t1 = time.time()
    block = 0
    for i in range(h*w):
        if board[i/w][i%w] == '2':
            block += 1
    proj = [0 for i in range(h*w)] # board -> mat
    projb = [0 for i in range(h*w-block)] # mat -> board
    num = 0
    for i in range(h*w):
        if board[i/w][i%w] != '2':
            proj[i] = num
            projb[num] = i
            num += 1
    fi = open('crossoutput.txt', 'r')
    res = fi.readline()
    print 'gauss time:', t1 - t2
    resarr = ['0' for i in range(h*w)]
    # should be inserting 0 into block positions
    # putting the return value into rite pos' instead is fine
    for i in range(len(res)):
        resarr[projb[i]] = res[i]
    res = ''
    for s in resarr:
        res += s
    sol = 'lvl=' + level + '&sol='  + res
    print 'get result time:', time.time() - t1
    return sol

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

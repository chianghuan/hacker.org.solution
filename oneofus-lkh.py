
#!/usr/bin/python27

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

problemUrl = 'http://www.hacker.org/oneofus/index.php'
username = ''
password = ''

def initAcc():
    f = open('account.pass', 'r')
    global username, password
    username = f.readline().strip()
    password = f.readline().strip()
    f.close()

def getstr(x, y, pos):
    xp = (pos - 1) % x
    yp = (pos - 1) / x
    return str.format('%X,%X' % (xp, yp)) #str(xp)+','+str(yp)

def mkurl(sol = None):
    if sol != None:
        sol = '&path=' + sol
    else:
        sol = ''
    return problemUrl + '?name=' + username + \
            '&password=' + password + sol

def nextLevel(sol):
    # post the request
    req = urllib2.Request(problemUrl)
    reqdata = 'name=' + username + '&password=' + password
    if sol != None:
        reqdata = reqdata + '&' + urllib.urlencode({'path':sol})
    req.add_data(reqdata)
    levelUrl = urllib2.urlopen(req)
    # get content
    pageText = levelUrl.read()
    seobj = re.search(r'FlashVars=".*?"', pageText)
    if seobj == None:
        print pageText
        return None
    args = seobj.group()[11:].strip('"').split('&')
    # XXX find my id on page... to get level number
    seobj = re.search(r'userid=26845.*?<', pageText)
    level = ''
    if seobj != None:
        level = seobj.group()
        seobj = re.search(r'>.*?<', level)
        level = seobj.group()[1:-1]
    # XXX the code above is not portable
    x = y = 0
    board = ''
    for arg in args:
        aname, aval = arg.split('=')
        if aname == 'x':
            x = int(aval)
        elif aname == 'y':
            y = int(aval)
        elif aname == 'board':
            board = aval
    return x, y, board, int(level) + 1

def checkCon(x, y, a, b):
    a1 = int(a) % x - 1
    a2 = int(a - 1) / x
    b1 = int(b) % x - 1
    b2 = int(b - 1) / x
    return a1 == b1 or a2 == b2

def getres(x, y):
    f = open('res.txt', 'r')
    for i in range(6):
        f.readline()
    ret = []
    res = ''
    while True:
        xx = int(f.readline())
        if xx == -1:
            break
        ret += [xx]
    # check conn, if not, join head-tail
    pp = -1
    for (i, j) in enumerate(ret):
        if i == len(ret) - 1:
            continue
        if checkCon(x, y, j, ret[i + 1]) == False:
            ret = ret[i+1:] + ret[0:i+1]
            break
    for xx in ret:
        res += getstr(x, y, xx) + '_'
    f.close()
    return res[0:-1]

def geninput(x, y, board, level):
    print 'board string len: ', len(board)
    print 'solving level by LKH solver: ', level
    f = open('input.hcp', 'w')
    f.write('NAME:input\n')
    f.write('TYPE:HCP\n')
    f.write('DIMENSION:%d\n' % (x * y))
    f.write('EDGE_DATA_FORMAT:EDGE_LIST\n')
    f.write('EDGE_DATA_SECTION\n')
    for i in range(1, x + 1):
        for j in range(1, y + 1):
            st = (j - 1) * x + i - 1
            for m in range(i + 1, x + 1):
                # (m, j)
                tar = (j - 1) * x + m - 1
                if board[st * 4 : st * 4 + 2] == board[tar * 4 : tar * 4 + 2] or \
                        board[st * 4 + 2 : st * 4 + 4] == board[tar * 4 + 2 : tar * 4 + 4]:
                    f.write('%d %d\n' % (st + 1, tar + 1))
                    f.write('%d %d\n' % (tar + 1, st + 1))
            for n in range(j + 1, y + 1):
                # (i, n)
                tar = (n - 1) * x + i - 1
                if board[st * 4 : st * 4 + 2] == board[tar * 4 : tar * 4 + 2] or \
                        board[st * 4 + 2 : st * 4 + 4] == board[tar * 4 + 2 : tar * 4 + 4]:
                    f.write('%d %d\n' % (st + 1, tar + 1))
                    f.write('%d %d\n' % (tar + 1, st + 1))
    f.write('-1\n')
    f.write('EOF\n')
    f.close()

def lkh():
    proc = subprocess.Popen('lkh.exe param.txt', \
            shell = False, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    while True:
        time.sleep(0.1)
        if proc.poll() != None:
            break
        while True:
            line = proc.stdout.readline()
            if line == None:
                break
            if '"res.txt"' in line and 'done' in line:
                proc.terminate()
                return None
    return None

if __name__ == "__main__":
    lastSol = None
    initAcc()
    while True:
        t1 = time.time()
        retry = 10
        doretry = True
        retvar = None
        while doretry and retry > 0:
            retry = retry - 1
            doretry = False
            try:
                retvar = nextLevel(lastSol)
            except Exception as exc:
                doretry = True
                print exc
                time.sleep(2)
            finally:
                pass
        t2 = time.time()
        if retvar == None:
            break
        print ''
        print 'retrived time(seconds):', t2 - t1
        # print retvar
        print 'level size: ', retvar[0], retvar[1]
        geninput(*retvar)
        lkh()
        lastSol = getres(retvar[0], retvar[1])
        # print 'solved:', lastSol
        t3 = time.time()
        print 'solved time(seconds):', t3 - t2
    print 'Program terminated'

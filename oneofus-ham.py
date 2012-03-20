#!/usr/bin/python27

import urllib
import urllib2
import httplib
import base64
import random
import time
import math
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

def mkurl(sol = None):
    global username, password
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

def addEdge(lnk, src, tar, nodes, alloc):
    nodes[alloc][1] = lnk[src][1]
    nodes[alloc][0] = tar
    lnk[src][0] = lnk[src][0] + 1
    lnk[src][1] = alloc

def sortEdges(lnk, nodes, x, y):
    for i in range(1, 1 + x * y):
        if lnk[i][0] <= 1:
            continue
        n = lnk[i][0]
        cur = lnk[i][1]
        while n > 1:
            n = n - 1
            mx, mxp = lnk[nodes[cur][0]][0], cur
            nex = nodes[cur][1]
            while nex != 0:
                if nodes[nex][0] < mx:
                    mx, mxp = lnk[nodes[nex][0]], nex
                nex = nodes[nex][1]
            if mxp != cur:
                tmp = nodes[cur][0]
                nodes[cur][0] = nodes[mxp][0]
                nodes[mxp][0] = tmp
            cur = nodes[cur][1]
    
def construct(x, y, board):
    # make graph link-table
    nodecount = (x + 1) * (y + 1)
    nodes = [[0, 0] for i in range(nodecount * nodecount * 2)] # node, next
    lnk = [[0, 0] for i in range((x + 1) * (y + 1))] # count, next
    alloc = 1
    for i in range(1, x + 1):
        for j in range(1, y + 1):
            st = (j - 1) * x + i - 1
            for m in range(i + 1, x + 1):
                # (m, j)
                tar = (j - 1) * x + m - 1
                if board[st * 2] == board[tar * 2] or \
                        board[st * 2 + 1] == board[tar * 2 + 1]:
                    addEdge(lnk, st + 1, tar + 1, nodes, alloc)
                    alloc = alloc + 1
                    addEdge(lnk, tar + 1, st + 1, nodes, alloc)
                    alloc = alloc + 1
            for n in range(j + 1, y + 1):
                # (i, n)
                tar = (n - 1) * x + i - 1
                if board[st * 2] == board[tar * 2] or \
                        board[st * 2 + 1] == board[tar * 2 + 1]:
                    addEdge(lnk, st + 1, tar + 1, nodes, alloc)
                    alloc = alloc + 1
                    addEdge(lnk, tar + 1, st + 1, nodes, alloc)
                    alloc = alloc + 1
    return lnk, nodes, alloc / 2

def solve(x, y, board, level):
    print 'board string len: ', len(board)
    print 'solving level by SEARCH: ', level
    lnk, nodes, m = construct(x, y, board)
    sortEdges(lnk, nodes, x, y)
    #sort by degree
    slist = [(lnk[i][0], i) for i in range(1, 1 + x * y)]
    slist.sort()
    #solve it
    fin = (1L << (x * y)) - 1
    for dummy, node in slist:
        ret = dfsSolve(x, y, lnk, nodes, 0L, node, fin)
        if ret != None:
            return getstr(x, y, node) + ret
    return None

def getstr(x, y, pos):
    xp = (pos - 1) % x
    yp = (pos - 1) / x
    return str.format('%X,%X' % (xp, yp)) #str(xp)+','+str(yp)

def dfsSolve(x, y, lnk, nodes, mark, node, fin):
    mark = mark | (1L << (node - 1))
    if mark == fin:
        return ''
    cur = lnk[node][1]
    ret = None
    xlist = []
    while cur != 0:
        lnk[nodes[cur][0]][0] = lnk[nodes[cur][0]][0] - 1
        xlist = xlist + [(lnk[nodes[cur][0]][0], nodes[cur][0])]
        cur = nodes[cur][1]
    xlist.sort()
    for count, nodenum in xlist:
        if (mark & (1L << (nodenum - 1))) == 0L:
            ret = dfsSolve(x, y, lnk, nodes, mark, nodenum, fin)
        if ret != None:
            return '_' + getstr(x, y, nodenum) + ret
    while cur != 0:
        lnk[nodes[cur][0]][0] = lnk[nodes[cur][0]][0] + 1
        cur = nodes[cur][1]
    return None

def hashList(li):
    tot = 0
    for i, s in enumerate(li):
        tot += s * i
    return tot % 1000000

def hamSolve(x, y, lnk, nodes, fr, to, m, fin):
    n = x * y
    d = 2 * int(m) / n
    T = int(math.log(n) / (math.log(d) - math.log(math.log(d)))) + 2 
    k = 1
    P = [[] for i in range(x * y + 2)]
    P[1] = [fr, to]
    Q = dict()
    CQ = dict()
    # here begins L1
    while True:
        Q[1] = P[k]
        s = 1
        t = 1
        CQ[hashList(Q[1])] = 0
        if k == x * y - 1:
            return P[k]
        L1 = False
        while True and L1 == False:
            for i in [0, -1]:
                w = Q[s][i]
                # check endpoint out-edge
                cur = lnk[w][1]
                while cur != 0:
                    xx = nodes[cur][0]
                    if xx != 0 and xx not in Q[s]:
                        # extension
                        if i == 0:
                            P[k + 1] = [xx] + Q[s]
                        else:
                            P[k + 1] = Q[s] + [xx]
                        k = k + 1
                        L1 = True
                        break
                    elif xx == Q[s][-1-i]:
                        # rotate
                        u = 0
                        fi = 0
                        # ddd = [dd for dd in enumerate(Q[s])]
                        # random.shuffle(ddd)
                        mn = 100000
                        for pos, num in enumerate(Q[s]):
                        # for pos in range(len(Q[s]) - 1, -1, -1):
                        # for pos, num in ddd:
                            num = Q[s][pos]
                            curp = lnk[num][1]
                            while curp != 0:
                                if nodes[curp][0] not in Q[s]:
                                    tmpfi = nodes[curp][0]
                                    if lnk[tmpfi][0] < mn:
                                        mn = lnk[tmpfi][0]
                                        fi = tmpfi
                                        u = pos
                                        break
                                # if fi != 0:
                                #    break
                                curp = nodes[curp][1]
                            # if fi != 0:
                            #    u = pos
                            #    break
                        P[k + 1] = [fi] + Q[s][u:] + Q[s][0:u]
                        k = k + 1
                        L1 = True
                        break
                    else:
                        t = t + 1
                        xp = Q[s].index(xx)
                        # rotate
                        if i == -1:
                            Q[t] = Q[s][0:xp + 1] + Q[s][-1:xp:-1] 
                        else:
                            tmp = Q[s][0:xp]
                            tmp.reverse()
                            Q[t] = tmp + Q[s][xp:] 
                        CQ[hashList(Q[t])] = CQ[hashList(Q[s])] + 1
                    cur = nodes[cur][1]
                if L1 == True:
                    break
            if L1 == True:
                break
            s = s + 1
            if CQ[hashList(Q[s])] >= 6 * T + 1:
                return None
        # L1 ends here
    return None

            
def solve2(x, y, board, level):
    print 'board string len: ', len(board)
    print 'solving level by HAM: ', level
    lnk, nodes, m = construct(x, y, board)
    sortEdges(lnk, nodes, x, y)
    #sort by degree
    slist = [(lnk[i][0], i) for i in range(1, 1 + x * y)]
    slist.sort()
    #solve it
    fin = (1L << (x * y)) - 1
    res = None
    for dummy, node in slist:
        suc = False
        to = lnk[node][1]
        while suc == False and to != 0:
            tar = nodes[to][0]
            ret = hamSolve(x, y, lnk, nodes, node, tar, m, fin)
            if ret != None:
                res = ret
                suc = True
            to = nodes[to][1]
        if suc:
            break
    if res != None:
        st = ''
        for i in res:
            st += getstr(x, y, i) + '_'
        return st[0:-1]
    return None

if __name__ == "__main__":
    initAcc()
    lastSol = None
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
        print retvar
        for i in range(10):
            lastSol = solve2(*retvar)
            if lastSol == None:
                print 'no solution found! times:', i
                t3 = time.time()
                print 'time(seconds):', t3 - t2
                t2 = t3
            else:
                break
        lastSol = solve(*retvar)
        t3 = time.time()
        print 'solved:', lastSol
        print 'time(seconds):', t3 - t2
    print 'Program terminated'

#! /usr/bin/env python3

import random, pprint

pp = pprint.PrettyPrinter(indent=4)

print('### GENERATE TEST DATA ###')
data = []
for x in range(random.randint(5, 10)):
    data.append([])
    for y in range(random.randint(1, 10)):
        if x == 0: y += 1
        data[x].append({'m':'{}.{}'.format(x,y)})
print('data: ')
pp.pprint(data)

"""
# VERSION SEQUENCE

+--[0.1 .. 0.m] = data[0]
|
+--[1.0 .. 1.m] = data[1]
|
+--[2.0 .. 2.m] = data[2]
|
+--[3.0 .. 3.m] = data[3]
|
+--[4.0 .. 4.m] = data[4]
.
.
+--[n.0 .. n.m] = data[n]

###################################
# INITIAL STAGE, NO MILESTONE YET #
###################################

CONDITION
    x == 0 and y == 0

SAMPLE VALUES
    x = 0
    y = 0

CONTEMPLATION
    n=0; m=1    Δn = n = 0; Δm = m = 1
    n=1; m=0    Δn = n = 1; Δm = len(data[0]) + m + 1
    n=2; m=0    Δn = n = 2; Δm = (∑len(data[s]))+m+1, s=n-1
    n=i; m=j    Δn = n = i; Δm = (∑len(data[s]))+j+1, s=i-1

CODE
    Δm = sum(len(data[s]) for s in range(n)) + m

TEST
"""
print()
print('### TEST V0.0 DELTA CALCULATION ###')
x = 0; y = 0
print('x:',x,'y:',y)

#### ACTUAL CODE ####
if x == 0 and y == 0:
    for n in range(len(data)):
        for m in range(len(data[n])):
            Δn = n
            Δm = sum(len(data[s]) for s in range(n)) + m
#### END ACTUAL CODE ####

            print('n:',n,'m:',m,'Δn:',Δn,'Δm:',Δm)

"""
######################################################################
# VERSION 0.5, LEN(DATA[0]) = 9, LEN(DATA[1]) = 6, LEN(DATA[2]) = 12 #
######################################################################

CONDITION
    x=0 && y>0 && y<len(data[0])

SAMPLE VALUES
    x=0
    y=5

EXAMPLES
    n=0; m=1    Δn = n = 0; Δm = m-y = -4
    n=0; m=5    Δn = n = 0; Δm = m-y = 0
    n=0; m=9    Δn = n = 0; Δm = m-y = 9-5 = 4
    n=1; m=0    Δn = n = 1; Δm = len(data[0]) - y + m + 1 = 9-5+0+1 = 5
    n=2; m=6    Δn = n = 2; Δm = (∑len(data[1->s])) + len(data[0]) - y + m + 1, s=n-1 =

DELTAS

"""

















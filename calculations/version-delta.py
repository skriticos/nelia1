#! /usr/bin/env python3

import random, pprint

pp = pprint.PrettyPrinter(indent=4)

print('### GENERATE TEST DATA ###')
data = []
for x in range(random.randint(5, 10)):
    data.append([])
    for y in range(random.randint(5, 10)):
        if x == 0: y += 1
        data[x].append({'m':'{}.{}'.format(x,y)})
print('data: ')
pp.pprint(data)

"""
# VERSION SEQUENCE

+--[0.1 .. 0.m(0)] = data[0]
|
+--[1.0 .. 1.m(1)] = data[1]
|
+--[2.0 .. 2.m(2)] = data[2]
|
+--[3.0 .. 3.m(3)] = data[3]
|
+--[4.0 .. 4.m(4)] = data[4]
.
.
+--[n.0 .. n.m(n)] = data[n]

"""

####################### UNIFIED MODEL ##########################################

x1 = 2
x2 = random.randint(2, len(data)-2)
x3 = len(data)-1
y11 = 0
y12 = len(data[x1])-2
y13 = len(data[x1])-1
y21 = 0
y22 = len(data[x2])-2
y23 = len(data[x2])-1
y31 = 0
y32 = len(data[x3])-2
y33 = len(data[x3])-1
test_data = (
    (0,0),
    (0,1), (0,len(data[0])-2), (0, len(data[0])-1),
    (1,0), (1,len(data[1])-2), (1, len(data[1])-1),
    (x1, y11), (x1, y12), (x1, y13),
    (x2, y21), (x2, y22), (x2, y23),
    (x3, y31), (x3, y32), (x3, y33))

for x,y in test_data:
    print('\nTEST RUN WITH..\n', 'x:',x,'y:',y)

    # loop through major versions
    Δn = 0
    for n in range(len(data)):
        Δn = n - x

        # loop through minor versions
        Δm = 0
        for m in range(len(data[n])):

            # 0.x series starts with 0.1 instead of 0.0
            if n == 0:
                m += 1

            # current version = 0.0 (no milestones reached)
            if x == 0 and y == 0:
                if n == 0:
                    Δm = m
                if n > 0:
                    Δm = sum(len(data[s]) for s in range(n)) + m + 1
            # current version = 0.y, y>0
            if x == 0 and y > 0:
                if n > 0:
                    Δm = sum(len(data[s]) for s in range(1,n)) + m + len(data[0]) - y + 1
                else:
                    Δm = m - y
            # current version = 1.y, y>=0
            if x == 1:
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * (y + (len(data[0])-m))
                    if n == 0:
                        Δm -= 1
            # current major version > 1
            if x > 1:
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * (
                        (  len(data[n]) - m)
                         + sum(len(data[s]) for s in range(n+1, x))
                         + y  )
                    if n == 0:
                        Δm -= 1

            # compute completion symbol
            if Δm > 1:
                sign = '+'
                icon = '◇'
            if Δm == 1:
                sign = '+'
                icon = '◈'
            if Δm == 0:
                sign = ''
                icon = '◆'
            if Δm < 0:
                sign = '-'
                icon = '◆'

            # compute major and minor version combined delta
            # notice how this has nothing to do with floating point
            # instead it's two deltas, major, and combined minor
            Δnm = '{}{},{}'.format(sign, abs(Δn), abs(Δm))

            print('n:',n,'m:',m,'\tΔn:',Δn,'Δm:',Δm,'\tΔnm:', Δnm, '\ticon:',icon)










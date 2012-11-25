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

##################### x = 0, y = 0 #############################################

# NOTE: X, Y     ARE THE CURRENT VERSION
#       N, M     ARE THE LOOP COUNTERS FOR THE VERSIONS
#       ΔN, ΔM   ARE THE VERSION DELTAS

print()
print('### TEST V0.0 DELTA CALCULATION ###')
x = 0; y = 0
print('x:',x,'y:',y)

#### ACTUAL CODE ####

if x == 0 and y == 0:
    Δn = 0
    for n in range(len(data)):
        Δn = n
        Δm = 0
        for m in range(len(data[n])):
            Δm = sum(len(data[s]) for s in range(n)) + m
            
#### END ACTUAL CODE ####

            print('n:',n,'m:',m,'Δn:',Δn,'Δm:',Δm)

####################### x = 0, y > 0 ###########################################

print()
print('### TEST V0.1-0.n(0) DELTA CALCULATION ###')
test_data = ((0,1), (0,len(data[0])-2), (0, len(data[0])-1))

for x,y in test_data:
    print('\nTEST RUN WITH..\n', 'x:',x,'y:',y)

#### ACTUAL CODE ####

    if x == 0 and y > 0:
        Δn = 0
        for n in range(len(data)):
            Δn = n
            Δm = 0
            for m in range(len(data[n])):
                if n > 0:
                    Δm = sum(len(data[s]) for s in range(1,n)) + m + len(data[0]) - y
                else:
                    Δm = m - y
                    
#### END ACTUAL CODE ####                    
                    
                print('n:',n,'m:',m,'Δn:',Δn,'Δm:',Δm)

####################### x = 1 ##################################################

print()
print('### TEST V1.0-0.n(1) DELTA CALCULATION ###')
test_data = ((1,0), (1,len(data[1])-2), (1, len(data[1])-1))

for x,y in test_data:
    print('\nTEST RUN WITH..\n', 'x:',x,'y:',y)

#### ACTUAL CODE ####

    if x == 1:
        Δn = 0
        for n in range(len(data)):
            Δn = n
            Δm = 0
            for m in range(len(data[n])):
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * y - (len(data[0])-m)

#### END ACTUAL CODE ####                    
                    
                print('n:',n,'m:',m,'Δn:',Δn,'Δm:',Δm)

####################### x > 1, y >= 0 ##########################################

print()
print('### TEST HIGHER DELTA CALCULATION ###')
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
    (x1, y11), (x1, y12), (x1, y13),
    (x2, y21), (x2, y22), (x2, y23),
    (x3, y31), (x3, y32), (x3, y33))

print ('\nTEST 3: X>1; TEST DATA:')
pp.pprint(test_data)
for x,y in test_data:
    print('\nTEST RUN WITH..\n', 'x:',x,'y:',y)

#### ACTUAL CODE ####

    if x > 1:
        Δn = 0
        for n in range(len(data)):
            Δn = n
            Δm = 0
            for m in range(len(data[n])):
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * (
                        (  len(data[n]) - m) 
                         + sum(len(data[s]) for s in range(n+1, x))
                         + y
                        )

#### END ACTUAL CODE ####                    
                    
                print('n:',n,'m:',m,'   Δn:',Δn,'Δm:',Δm)

####################### UNIFIED MODEL ##########################################

"""
    Δn = 0
    for n in range(len(data)):
        Δn = n
        Δm = 0
        for m in range(len(data[n])):
            if x == 0 and y == 0:
                Δm = sum(len(data[s]) for s in range(n)) + m
            if x == 1:
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * (y + (len(data[0])-m))
            if x > 1:
                if n == x:
                    Δm = m - y
                if n > x:
                    Δm = sum(len(data[s]) for s in range(x+1,n)) + m + len(data[x]) - y
                if n < x:
                    Δm = -1 * (
                        (  len(data[n]) - m) 
                         + sum(len(data[s]) for s in range(n+1, x))
                         + y
                        )            
"""


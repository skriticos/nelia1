#! /usr/bin/env python3


data = [
    [{}, {}],     # 0.1, 0.2 - 0.x starts with 0.1
    [{}, {}],     # 1.0, 1.1
    [{}, {}, {}], # 2.0, 2.1, 2,1
    [{}, {}],     # 3.0, 3.1
    [{}, {}, {}], # 4.0, 4.1, 4.2
    [{}, {}, {}]  # 5.0, 5.1, 5.2
]


n = 2
m = 1

current = (n,m)
for major in range(len(data)):
    majd = -1 * (current[0] - major)
    for minor in range(len(data[major])):
        if major == 0:
            minor += 1

        print ('v{}.{} -> '.format(major,minor), end='')

        mind = 0
        if majd == 0:
            mind = -1 * (current[1] - minor)
        if majd > 0:
            print (majd, minor+1, end=';')

            # calculate majd > 0
            # 3.0 = rest of 2 + 1
            # 3.1 = rest of 2 + 2
            # 4.0 = rest of 2 + len(3) + 1
            # 4.1 = rest of 2 + len(3) + 2
            # 5.0 = rest of 2 + len(3) + len(4) + 1
            pass

        print ('\tres', majd, mind)


#!/usr/bin/env python
#
# Author: Ryan Roberts

from door import Door
from time import time
import sys

if __name__ == "__main__":
    test = Door()
    test.start_new_trial(0)
    print(sys.argv[1])
    if(int(sys.argv[1]) == 0):
        try:
            while True:
                print(test.collect_data().angle)
        except KeyboardInterrupt:
            test.reset()
    elif(int(sys.argv[1]) == 1):
        test_time = float(sys.argv[2])
        timer = time() + test_time
        while (time() <= timer):
            print(test.collect_data().angle)
        test.reset()
    else:
        raise Exception("Not valid first parameter")
    
# Test opening RM's and activating slots using Jordan's code!

from TestStand import TestStand as ts

activeSlots = [2,3,24,25,26]
myTS = ts(activeSlots)
print myTS.RMs

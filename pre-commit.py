#!/usr/bin/python
from utils import *
import time
product = getProduct()

oldRev = sys.argv[1]
newRev = sys.argv[2]
refName = sys.argv[3]

branches = getOpenBranches()
# unless the pushed reference is on the story branches or master, continue
if refName not in branches:
    sys.exit(0)
if newRev == '0000000000000000000000000000000000000000':
    # delete a branch
    sys.exit(0)
if oldRev == '0000000000000000000000000000000000000000':
	# pushing a new branch to remote
	sys.exit(0)

revListOuput = git(['rev-list', oldRev + '..' + newRev])
revList = revListOuput.split()

depth = 1
for r in revList:
    log = git(['rev-list', '--format=%B', '--max-count=1', r]) # %B revision number and message
    message = log.strip().split('\n')[1]
    if doesChangeNeedStoryNum(r):
         if not isCommitMessageValid(message, r, depth):
            sys.exit(1)
    depth = depth + 1

import fileinput, sys, subprocess, re, urllib2, urllib, os

url = "http://tools.integration.server/repository/git-broadcast"
def sendPost(author, message, revision, refName):
    dataDict = {'author': author, 'message': message, 'revision': revision,'refName': refName}
    data = urllib.urlencode(dataDict)
    req = urllib2.Request(url, data)
    f = urllib2.urlopen(req)
    response = f.read()
    print "response: " + response 
    f.close()
    
def git(args):
    args.insert(0, '/usr/local/bin/git')
    revListProcess = subprocess.Popen(args, stdout=subprocess.PIPE)
    return revListProcess.communicate()[0]

def infoLog(commitId, message):
    print commitId + '::INFO ' + message

def errorLog(commitId, message):
    print commitId + '::ERROR ' + message

def isCommitMessageValid(message, commitId, commitDepth):
    if len(message) == 0:
        errorLog('Empty commit messages are not permitted')
        return False

    if re.search('.*([a-zA-Z]{1,2}-[0-9]{4,5}).*', message) == None and re.search('.*(master).*', message) == None:
        errorLog(commitId, 'Invalid commit message:\n\n' + message + '\n')
        errorLog(commitId, 'Commit message must contain a story or task number in the following format: XX-12345')
        if commitDepth == 1:
            errorLog(commitId, 'Use git commit --amend')
        else:
            errorLog(commitId, 'Use git rebase -i ' + commitId + '^')
        return False

    infoLog(commitId, "Task number in commit looks good")
    return True

def doesChangeNeedStoryNum(commitId):
    tree = git(['diff-tree', '--no-commit-id', '--name-only','-r', commitId]) 
    return re.search('^(baseline|tools|movecars)/', tree.strip()) == None

def hasTwoParents(r):
    hashes = git(['show', '--pretty=%P', r]).strip().split()
    # print "hashes: " + ' '.join( hashes )
    return len(hashes) == 2 and len(hashes[0]) == len(hashes[1]) and len(hashes[0]) == 40

def getOtherParentName(r, knownBranchName = None):
    # print "get other parent name called: " + knownBranchName
    branches = git(['branch', '--contains', r + '^2'])
    # print '\nbranches: '
    # print branches + '\n';
    branches = branches.strip().split('\n');
    branches = [x.strip().replace('* ', '') for x in branches]
    if knownBranchName in branches:
        branches.remove(knownBranchName)
    if len(branches) == 0:
        return ''
    toReturn = branches.pop()
    # print toReturn
    return toReturn


def getOpenBranches():
    # get a list of open branches
    branches = git(['branch']).split('\n')
    branches = ['refs/heads/' + x.strip().replace('* ', '') for x in branches]
    return branches

def getProduct():
    dir = os.path.dirname(os.path.realpath(__file__))
    if 'CD' in dir:
        return 'CD'
    elif 'JT' in dir:
        return 'JT'
    else:
        return 'ProductUnknown'

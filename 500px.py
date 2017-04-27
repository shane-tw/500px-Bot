#!/usr/bin/env python

import requests, time, json, os
from bs4 import BeautifulSoup
from random import randint

scriptDirectory = os.path.abspath(os.path.dirname(__file__))
logDate = time.strftime('%Y-%m-%d')

userSession = requests.Session()
userSession.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
})

pendingFileName = 'pendingUsers.txt'
acceptedFileName = 'acceptedUsers.txt'
ignoredFileName = 'ignoredUsers.txt'

pendingFilePath = scriptDirectory + '/' + pendingFileName
acceptedFilePath = scriptDirectory + '/' + acceptedFileName
ignoredFilePath = scriptDirectory + '/' + ignoredFileName

logFileName = logDate + '_log.txt'
logFilePath = scriptDirectory + '/logs/'

loginParams = {
    'authenticity_token': '', # Don't change me
    'session[email]': '', # Change me
    'session[password]': '' # Change me
}

csrfHeaders = {
    'X-CSRF-Token': '',
    'X-Requested-With': 'XMLHttpRequest'
}

pendingFollowList = []
acceptedFollowList = []
ignoredFollowList = []

def printToLog(string):
    global logFilePath, logFileName
    logTime = time.strftime('%H:%M:%S')
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
    with open(logFilePath + logFileName, 'a+') as f:
        f.write(logTime + ' - ' + string + '\n')
    print(logTime + ' - ' + string)

def retrieveLists():
    global pendingFilePath, acceptedFilePath, ignoredFilePath
    global pendingFollowList, acceptedFollowList, ignoredFollowList
    if os.path.exists(pendingFilePath):
        with open(pendingFilePath, 'r') as f:
            pendingFollowList = json.loads(f.read())
    if os.path.exists(acceptedFilePath):
        with open(acceptedFilePath, 'r') as f:
            acceptedFollowList = json.loads(f.read())
    if os.path.exists(ignoredFilePath):
        with open(ignoredFilePath, 'r') as f:
            ignoredFollowList = json.loads(f.read())

def isUserPending(targetUserName):
    global pendingFollowList
    for i, v in enumerate(pendingFollowList):
        if v['name'] == targetUserName:
            return True
    return False

def isUserAccepted(targetUserName):
    global acceptedFollowList
    for i, v in enumerate(acceptedFollowList):
        if v['name'] == targetUserName:
            return True
    return False

def isUserIgnored(targetUserName):
    global ignoredFollowList
    userIgnored = False
    for i, v in enumerate(ignoredFollowList):
        if v['name'] == targetUserName:
            return True
    return False

def followUser(targetUserName):
    global userSession, numFollowsDone, csrfHeaders
    continueLoop = True
    while continueLoop:
        try:
            followResp = userSession.post('https://500px.com/' + targetUserName + '/follow', timeout = 5, headers = csrfHeaders)
            if followResp.status_code == 200:
                printToLog('Followed ' + targetUserName + '.')
                numFollowsDone += 1
                addUserToPendingList(targetUserName)
                continueLoop = False
            elif followResp.status_code == 404:
                printToLog('User ' + targetUserName + ' no longer exists. Skipped follow.')
                continueLoop = False
            elif followResp.status_code == 403:
                printToLog('Already followed ' + targetUserName + '.')
                continueLoop = False
            else:
                printToLog('A server error (' + str(followResp.status_code) + ') occured. Retrying...')
                printToLog('Error page: ' + followResp.url)
                time.sleep(5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
    time.sleep(20)

def addUserToPendingList(targetUserName):
    global pendingFollowList, pendingFilePath
    if targetUserName in pendingFollowList:
        return
    pendingFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(pendingFilePath, 'w') as f:
        f.write(json.dumps(pendingFollowList))

def addUserToAcceptedList(targetUserName):
    global acceptedFollowList, acceptedFilePath
    if targetUserName in acceptedFollowList:
        return
    acceptedFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(acceptedFilePath, 'w') as f:
        f.write(json.dumps(acceptedFollowList))

def addUserToIgnoredList(targetUserName):
    global ignoredFollowList, ignoredFilePath
    if targetUserName in ignoredFollowList:
        return
    ignoredFollowList.append({'name': targetUserName, 'time_followed': time.time()})
    with open(ignoredFilePath, 'w') as f:
        f.write(json.dumps(ignoredFollowList))

def unfollowUser(targetUserName):
    global userSession, csrfHeaders
    continueLoop = True
    while continueLoop:
        try:
            unfollowResp = userSession.post('https://500px.com/' + targetUserName + '/unfollow', timeout = 5, headers = csrfHeaders)
            if unfollowResp.status_code == 200:
                printToLog('Unfollowed ' + targetUserName + '.')
                continueLoop = False
            elif unfollowResp.status_code == 404:
                printToLog('User ' + targetUserName + ' no longer exists. Skipped unfollow.')
                continueLoop = False
            else:
                printToLog('A server error (' + str(unfollowResp.status_code) + ') occured. Retrying...')
                printToLog('Error page: ' + unfollowResp.url)
                time.sleep(5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
    time.sleep(20)

def getFollowing():
    global myUserInfo, csrfHeaders
    pageNum = 1
    following = []
    while True:
        followingPage = requestWebPage('GET', 'https://api.500px.com/v1/users/' + str(myUserInfo['id']) + '/friends?fullformat=0&page=' + str(pageNum) + '&rpp=50', headers = csrfHeaders)
        followingPage_json = json.loads(followingPage.text)
        following += followingPage_json['friends']
        if pageNum == followingPage_json['friends_pages']:
            break
        pageNum += 1
        time.sleep(20)
    return following

def getFollowers():
    global myUserInfo
    pageNum = 1
    followers = []
    while True:
        followersPage = requestWebPage('GET', 'https://api.500px.com/v1/users/' + str(myUserInfo['id']) + '/followers?fullformat=0&page=' + str(pageNum) + '&rpp=50')
        followersPage_json = json.loads(followersPage.text)
        followers += followersPage_json['followers']
        if pageNum == followersPage_json['followers_pages']:
            break
        pageNum += 1
        time.sleep(20)
    return followers

def requestWebPage(method, url, data = {}, headers = {}, checkStatusCode = True):
    global userSession
    while True:
        try:
            response = userSession.request(method, url, data = data, headers = headers, timeout = 5)
        except requests.exceptions.RequestException:
            printToLog('Web page timed out. Retrying...')
            time.sleep(5)
            continue
        if checkStatusCode and response.status_code != 200:
            printToLog('A server error (' + str(response.status_code) + ') occured. Retrying...')
            printToLog('Error page: ' + response.url)
            time.sleep(5)
            continue
        return response

def removeUserFromPendingList(targetUserName):
    global pendingFollowList, pendingFilePath
    for i, v in enumerate(list(pendingFollowList)):
        if v['name'] == targetUserName:
            pendingFollowList.remove(v)
            break
    with open(pendingFilePath, 'w') as f:
        f.write(json.dumps(pendingFollowList))

def removeUserFromAcceptedList(targetUserName):
    global acceptedFollowList, acceptedFilePath
    for i, v in enumerate(list(acceptedFollowList)):
        if v['name'] == targetUserName:
            acceptedFollowList.remove(v)
            break
    with open(acceptedFilePath, 'w') as f:
        f.write(json.dumps(acceptedFollowList))

def removeUserFromIgnoredList(targetUserName):
    global ignoredFollowList, ignoredFilePath
    for i, v in enumerate(list(ignoredFollowList)):
        if v['name'] == targetUserName:
            ignoredFollowList.remove(v)
            break
    with open(ignoredFilePath, 'w') as f:
        f.write(json.dumps(ignoredFollowList))

# Retrieving the list of currently pending followed users by the bot.

retrieveLists()

# Time to remove anyone in any list for more than a week.

currentTime = time.time()
for i, v in enumerate(list(acceptedFollowList)):
    if currentTime - v['time_followed'] > 604800:
        continue
    acceptedFollowList.remove(v)
    with open(acceptedFilePath, 'w') as f:
        f.write(json.dumps(acceptedFollowList))

for i, v in enumerate(list(ignoredFollowList)):
    if currentTime - v['time_followed'] > 604800:
        continue
    ignoredFollowList.remove(v)
    with open(ignoredFilePath, 'w') as f:
        f.write(json.dumps(ignoredFollowList))

# This is used in order to obtain the authenticity token required for logging in.

loginPage = requestWebPage('GET', 'https://500px.com/login')
printToLog('Retrieved login page.')
time.sleep(20)

loginPage_soup = BeautifulSoup(loginPage.text, 'html.parser')
loginParams['authenticity_token'] = loginPage_soup.find('meta', {'name': 'csrf-token'}).get('content')
csrfHeaders['X-CSRF-Token'] = loginParams['authenticity_token']

# This is the actual login request.

userLogin = requestWebPage('POST', 'https://api.500px.com/v1/session', data = loginParams)
printToLog('Logged in successfully.')
time.sleep(20)

# Getting my user info from login response.

myUserInfo = json.loads(userLogin.text)['user']

# Time to see who has actually bothered following us.

pendingUserNames = [pendingFollowUser['name'] for pendingFollowUser in pendingFollowList]

followers = getFollowers()
printToLog('Obtained a list of followers.')
following = getFollowing()
printToLog('Obtained a list of people we\'re following.')

for followingUser in following:
    if followingUser['username'] in pendingUserNames:
        continue
    if any(follower['username'] == followingUser['username'] for follower in followers):
        continue
    unfollowUser(followingUser['username'])
    addUserToIgnoredList(followingUser['username'])
    printToLog(followingUser['username'] + ' isn\'t following you and isn\'t pending. Ignored and unfollowed.')
printToLog('Finished comparing followers against following.')

for follower in list(followers):
    currentTime = time.time()
    if not follower['username'] in pendingUserNames:
        followers.remove(follower)
        continue
    removeUserFromPendingList(follower['username'])
    addUserToAcceptedList(follower['username'])
    printToLog(follower['username'] + ' followed you. Accepted.')
    pendingUserNames.remove(follower['username'])
    followers.remove(follower)

for follower in list(pendingFollowList):
    currentTime = time.time()
    if currentTime - follower['time_followed'] <= 172800:
        continue
    removeUserFromPendingList(follower['name'])
    unfollowUser(follower['name'])
    addUserToIgnoredList(follower['name'])
    pendingUserNames.remove(follower['name'])
    printToLog(follower['name'] + ' didn\'t follow you. Ignored and unfollowed.')

printToLog('Review of followed users finished.')

# Time to view the up-and-coming and follow more people :)

pageNum = 1 # Do not change.
numFollowsWanted = 101 # 101 is the daily limit for follows, and any more than this fails. Don't increase.
numFollowsDone = 0 # Do not change.

while numFollowsDone < numFollowsWanted:
    upcomingPage = requestWebPage('GET', 'https://api.500px.com/v1/photos?feature=upcoming&include_states=false&page=' + str(pageNum) + '&rpp=50', headers = csrfHeaders)
    upcomingPage_json = json.loads(upcomingPage.text)
    for upcomingPhoto in upcomingPage_json['photos']:
        userName = upcomingPhoto['user']['username']
        if numFollowsDone == numFollowsWanted:
            break
        if not isUserPending(userName) and not isUserAccepted(userName) and not isUserIgnored(userName):
            followUser(userName)
        else:
            printToLog('Skipping ' + userName + '.')
    pageNum += 1
    time.sleep(20)
printToLog('Finished. No more users left to follow.')

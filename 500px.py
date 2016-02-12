import requests, time, json, os
from bs4 import BeautifulSoup
from random import randint

userSession = requests.Session()

login_params = {
	'authenticity_token': '',
	'session[email]': input('Whats your email?: '),
	'session[password]': input('Whats your password?: ')
}

generic_headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

csrf_headers = {
	'X-CSRF-Token': '',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': generic_headers['User-Agent']
}

pendingFollowList = []
acceptedFollowList = []
ignoredFollowList = []

def retrieveLists():
	global pendingFollowList, acceptedFollowList, ignoredFollowList
	if os.path.exists('pendingUsers.txt'):
		with open('pendingUsers.txt', 'r') as f:
			pendingFollowList = json.loads(f.read())
	if os.path.exists('acceptedUsers.txt'):
		with open('acceptedUsers.txt', 'r') as f:
			acceptedFollowList = json.loads(f.read())
	if os.path.exists('ignoredUsers.txt'):
		with open('ignoredUsers.txt', 'r') as f:
			ignoredFollowList = json.loads(f.read())

def isUserPending(targetUserName):
	global pendingFollowList
	userPending = False
	for i, v in enumerate(pendingFollowList):
		if v['name'] == targetUserName:
			userPending = True
			break
	return userPending

def isUserAccepted(targetUserName):
	global acceptedFollowList
	userAccepted = False
	for i, v in enumerate(acceptedFollowList):
		if v['name'] == targetUserName:
			userAccepted = True
			break
	return userAccepted

def isUserIgnored(targetUserName):
	global ignoredFollowList
	userIgnored = False
	for i, v in enumerate(ignoredFollowList):
		if v['name'] == targetUserName:
			userIgnored = True
			break
	return userIgnored

def followUser(targetUserName):
	global userSession, numFollowsDone
	continueLoop = True
	while continueLoop:
		try:
			followResp = userSession.post('https://500px.com/' + targetUserName + '/follow', timeout = 5, headers = csrf_headers)
			if followResp.status_code == 200:
				print('Followed ' + targetUserName + '.')
				numFollowsDone += 1
				addUserToPendingList(targetUserName)
				continueLoop = False
			elif followResp.status_code == 403:
				print('Already followed ' + targetUserName + '.')
				continueLoop = False
			else:
				print('A server error (' + str(followResp.status_code) + ') occured. Retrying...')
				print('Error page: ' + followResp.url)
				time.sleep(5)
		except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
	time.sleep(20)

def addUserToPendingList(targetUserName):
	global pendingFollowList
	pendingFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open('pendingUsers.txt', 'w') as f:
		f.write(json.dumps(pendingFollowList))

def addUserToAcceptedList(targetUserName):
	global acceptedFollowList
	acceptedFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open('acceptedUsers.txt', 'w') as f:
		f.write(json.dumps(acceptedFollowList))

def addUserToIgnoredList(targetUserName):
	global ignoredFollowList
	ignoredFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open('ignoredUsers.txt', 'w') as f:
		f.write(json.dumps(ignoredFollowList))

def userExists(targetUserName):
	global userSession
	continueLoop = True
	while continueLoop:
		try:
			userResp = userSession.get('https://500px.com/' + targetUserName, timeout = 5, headers = generic_headers)
			if userResp.status_code == 200:
				return True
			elif userResp.status_code == 404:
				return False
			else:
				print('A server error (' + str(userResp.status_code) + ') occured. Retrying...')
				print('Error page: ' + userResp.url)
				time.sleep(5)
		except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
	time.sleep(20)

def unfollowUser(targetUserName):
	global userSession
	continueLoop = True
	while continueLoop:
		try:
			unfollowResp = userSession.post('https://500px.com/' + targetUserName + '/unfollow', timeout = 5, headers = csrf_headers)
			if unfollowResp.status_code == 200:
				print('Unfollowed ' + targetUserName + '.')
				continueLoop = False
			else:
				print('A server error (' + str(unfollowResp.status_code) + ') occured. Retrying...')
				print('Error page: ' + unfollowResp.url)
				time.sleep(5)
		except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
	time.sleep(20)

def removeUserFromPendingList(targetUserName):
	global pendingFollowList
	for i, v in enumerate(list(pendingFollowList)):
		if v['name'] == targetUserName:
			pendingFollowList.remove(v)
			break
	with open('pendingUsers.txt', 'w') as f:
		f.write(json.dumps(pendingFollowList))

def removeUserFromAcceptedList(targetUserName):
	global acceptedFollowList
	for i, v in enumerate(list(acceptedFollowList)):
		if v['name'] == targetUserName:
			acceptedFollowList.remove(v)
			break
	with open('acceptedUsers.txt', 'w') as f:
		f.write(json.dumps(acceptedFollowList))

def removeUserFromIgnoredList(targetUserName):
	global ignoredFollowList
	for i, v in enumerate(list(ignoredFollowList)):
		if v['name'] == targetUserName:
			ignoredFollowList.remove(v)
			break
	with open('ignoredUsers.txt', 'w') as f:
		f.write(json.dumps(ignoredFollowList))

# Retrieving the list of currently pending followed users by the bot.

retrieveLists()

# Time to remove anyone in any list for more than a week.

currentTime = time.time()
for i, v in enumerate(list(acceptedFollowList)):
	if currentTime - v['time_followed'] > 604800:
		acceptedFollowList.remove(v)
		with open('acceptedUsers.txt', 'w') as f:
			f.write(json.dumps(acceptedFollowList))

for i, v in enumerate(list(ignoredFollowList)):
	if currentTime - v['time_followed'] > 604800:
		ignoredFollowList.remove(v)
		with open('ignoredUsers.txt', 'w') as f:
			f.write(json.dumps(ignoredFollowList))

# This is used in order to obtain the authenticity token required for logging in.

continueLoop = True
while continueLoop:
	try:
		loginPage = userSession.get('https://500px.com/login', timeout = 5, headers = generic_headers)
		if loginPage.status_code == 200:
			print('Retrieved login page.')
			continueLoop = False
		else:
			print('A server error (' + str(loginPage.status_code) + ') occured. Retrying...')
			print('Error page: ' + loginPage.url)
			time.sleep(5)
	except requests.exceptions.RequestException:
		print('Web page timed out. Retrying...')
		time.sleep(5)
time.sleep(20)

loginPage_soup = BeautifulSoup(loginPage.text, 'html.parser')
login_params['authenticity_token'] = loginPage_soup.find('meta', {'name': 'csrf-token'}).get('content')
csrf_headers['X-CSRF-Token'] = login_params['authenticity_token']

# This is the actual login request.

continueLoop = True
while continueLoop:
	try:
		userLogin = userSession.post('https://api.500px.com/v1/session', data = login_params, timeout = 5, headers = generic_headers)
		if userLogin.status_code == 200:
			print('Logged in successfully.')
			continueLoop = False
		else:
			print('A server error (' + str(userLogin.status_code) + ') occured. Retrying...')
			print('Error page: ' + userLogin.url)
			time.sleep(5)
	except requests.exceptions.RequestException:
		print('Web page timed out. Retrying...')
		time.sleep(5)
time.sleep(20)

# Getting my user info from login response.

myUserInfo = json.loads(userLogin.text)['user']

# Time to see who has actually bothered following us.

pageNum = 1
pendingUserNames = [pendingFollowUser['name'] for pendingFollowUser in pendingFollowList]
myFollowers_json = []

while True:
	try:
		myFollowers = userSession.get('https://api.500px.com/v1/users/' + str(myUserInfo['id']) + '/followers?fullformat=0&page=' + str(pageNum) + '&rpp=50', timeout = 5, headers = generic_headers)
		if myFollowers.status_code != 200:
			print('A server error (' + str(myFollowers.status_code) + ') occured. Retrying...')
			print('Error page: ' + myFollowers.url)
			time.sleep(5)
			continue
	except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
			continue
	tmpFollowers_json = json.loads(myFollowers.text)
	myFollowers_json += tmpFollowers_json['followers']
	if pageNum == tmpFollowers_json['followers_pages']:
		break
	pageNum += 1
	time.sleep(20)

for follower in list(myFollowers_json):
	currentTime = time.time()
	if not follower['username'] in pendingUserNames:
		myFollowers_json.remove(follower)
		continue
	removeUserFromPendingList(follower['username'])
	addUserToAcceptedList(follower['username'])
	print(follower['username'] + ' followed you. Accepted.')
	pendingUserNames.remove(follower['username'])
	myFollowers_json.remove(follower)

for follower in list(pendingFollowList):
	currentTime = time.time()
	if currentTime - follower['time_followed'] <= 172800:
		continue
	removeUserFromPendingList(follower['name'])
	if userExists(follower['name']):
		unfollowUser(follower['name'])
		addUserToIgnoredList(follower['name'])
	pendingUserNames.remove(follower['name'])
	print(follower['name'] + ' didn\'t follow you. Ignored and unfollowed.')
print('Review of followed users finished.')

# Time to view the up-and-coming and follow more people :)

pageNum = 1
numFollowsWanted = 101
numFollowsDone = 0

while numFollowsDone < numFollowsWanted:
	try:
		upcomingPage = userSession.get('https://api.500px.com/v1/photos?feature=upcoming&include_states=false&page=' + str(pageNum) + '&rpp=50', timeout = 5, headers = csrf_headers)
		if upcomingPage.status_code != 200:
			print('A server error (' + str(upcomingPage.status_code) + ') occured. Retrying...')
			print('Error page: ' + upcomingPage.url)
			time.sleep(5)
			continue
	except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
			continue
	upcomingPage_json = json.loads(upcomingPage.text)
	for upcomingPhoto in upcomingPage_json['photos']:
		if not isUserPending(myUserInfo['username']) and not isUserAccepted(myUserInfo['username']) and not isUserIgnored(myUserInfo['username']) and numFollowsDone < numFollowsWanted:
			followUser(upcomingPhoto['user']['username'])
		elif numFollowsDone >= numFollowsWanted:
			break
	pageNum += 1
	time.sleep(20)
print('Finished. No more users left to follow.')

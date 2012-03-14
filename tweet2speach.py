import tweetstream
import os
import json
import ConfigParser

import android

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
droid = android.Android()
droid.makeToast('starting tweet2speach!')
droid.webViewShow(os.path.join(ROOT_DIR, "config.html"))

c = ConfigParser.ConfigParser()
c.read('configuration.txt')
info_saved = False

if c.has_section('twitter'):
	droid.eventPost('readerState', 'loaded twitter account data from file')
	info_saved = True
else:
	c.add_section('twitter')
	droid.eventPost('readerState','Please, fill the user / pass form')


while True:
	result = droid.eventWaitFor('conf').result
	configuration = json.loads(result['data'])
	
	if info_saved:
		user = c.get('twitter', 'username')
		password = c.get('twitter', 'password')
	else:
		#plug the data from the form into variables
		user = configuration['username']
		password = configuration['password']
		
		c.set('twitter', 'username', user)
		c.set('twitter', 'password', password)
		
		with open('configuration.txt','wb') as configfile:
			c.write(configfile)

	hashtag = [configuration['hashtag']]

	controlReader = droid.eventWaitFor('controlReader').result
	state = controlReader['data']
	print state
	


	if state == 'True':
		droid.eventPost('readerState', 'Reader started')
		with tweetstream.FilterStream(user,password, track=hashtag) as stream:
			for tweet in stream:
				try:					
					t = tweet['text']
					t.encode('ascii','replace')
					droid.eventPost('tweet', t)
					droid.ttsSpeak(t)
				except:
					pass


	elif state == 'False':
		droid.eventPost('readerState', 'Reader stopped')



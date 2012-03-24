from collections import deque
import os
import android
import twitstream
import json

droid = android.Android()
to_read = deque([])

def readTweet():
	droid.eventPost('readerState', str(len(to_read)) + ' messages in queue')
	if len(to_read) > 0:
		try:
			tmp = to_read.popleft()
			droid.eventPost('tweet', tmp)
			droid.ttsSpeak(tmp)
		except Exception, err:
			droid.eventPost('error', err)
			pass

class Process(object):
	def __init__(self, keywords=[]):
		self.keywords = keywords

	def __call__(self, status):
		try:
			st = status['text'].encode('utf-8')
			to_read.append(st)

			if len(to_read) > 100:
				droid.eventPost('readerState', 'Cleaning queue')
				to_read.clear()
				droid.eventPost('readerState', 'Queue cleaned!')

			if not droid.ttsIsSpeaking()[1]:
				readTweet()
			else:
				pass
		except Exception, err:
			droid.eventPost('error', err)
			pass

if __name__ == '__main__':
	ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
	
	#initialize android api
	droid. makeToast('starting tweet2speach!')
	droid.webViewShow(os.path.join(ROOT_DIR, "interface.html"))
	
	hashtags = []

	result = droid.eventWaitFor('conf').result
	controlReader = droid.eventWaitFor('controlReader').result
	
	state = controlReader['data']
	configuration = json.loads(result['data'])
	user = configuration['username']
	password = configuration['password']
	hashtags.append(configuration['hashtag'])

	processTweet = Process(hashtags)

	#setup twitter connection
	if state:
		droid.eventPost('readerState','Reader started')
		stream = twitstream.track(user, password, processTweet, hashtags)
		stream.run()
	

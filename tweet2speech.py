# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2010 martinez-zea <http://martinez-zea.info>
#

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
			while len(to_read) > 0:
				if not droid.ttsIsSpaking()[1]:
					droid.eventPost('readerState', str(len(to_read)) + ' messages in queue')
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
	droid. makeToast('starting tweet2speech!')
	droid.webViewShow(os.path.join(ROOT_DIR, "gui/interface.html"))
	
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
	

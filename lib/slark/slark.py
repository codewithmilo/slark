import os
import json
import threading

try:
	import cPickle as pickle
except:
	import pickle

from appdirs import AppDirs
from lib.slark.slark_comm import SlarkComm
from lib.slark.slark_client import SlarkClient

# i stole this from a client, this should be gotten through the oauth flow (or something)
os.environ["SLACK_API_TOKEN"] = 

# location for local store
dirs = AppDirs('Slark', 'Milo')
store_dir = dirs.user_data_dir
store_path = store_dir + '/slark_model.pickle'


class Slark:
	def __init__(self, args=None):
		# im not sure where to put this, but it's probably better somewhere else
		self.MSG_HISTORY_LIMIT = 30
		# the usefulness of this as a separate class is dubious
		self.client = SlarkClient()

		self.api_token = os.environ["SLACK_API_TOKEN"]
		# setup a WS & API client
		self.comm = SlarkComm(self.api_token, args)
		self.comm.signals.connect(self.comm.signals, 'on-msg', self.updateMessages)

		# try to get data from our local store first
		setup = self.setup_from_store()
		if not setup:
			# get all the boot data from an rtm.start call
			self.boot = self.rtm_start()
			# the current channel in view, and its history.
			self.view = self.get_channel()

			# store the local model
			# do it in a thread so we don't need to wait for it
			store_thread = threading.Thread(target=self.store_model, daemon=True)
			store_thread.start()
		else:
			# since we have the data we need, just rtm.connect to get the WS url
			conn = self.comm.api_call('rtm.connect')
			self.setup_websocket(conn)


	def setup_from_store(self):
		# TODO make sure we look at the `latest_event_ts` to either redo rtm.start or pull from the eventlog
		try:
			store = open(store_path, 'rb')
		except FileNotFoundError:
			return False

		model = pickle.load(store)
		self.boot = model['boot']
		self.view = model['view']
		store.close()
		return True

	def rtm_start(self):
		reply = self.comm.api_call('rtm.start', simple_latest=True)

		self.setup_websocket(reply)

		return self.client.setup_boot(reply)

	def setup_websocket(self, rtm_res):
		if rtm_res['ok']:
			self.comm.set_ws_url(rtm_res['url'])
			self.comm.ws_connect()
		else:
			raise Exception(rtm_res.error)

	def get_channel(self, chan_id='', **args):

		view = {}

		if chan_id == '':
			channel_id = self.boot['general']['id']
			channel = self.boot['general']
		else:
			channel_id = chan_id
			channel = self.get_channel_by_id(channel_id)

		view['channel'] = channel

		# pretty low limit because terminal windows are small
		limit = args.get('limit', self.MSG_HISTORY_LIMIT)
		cursor = args.get('cursor', '')

		history = self.comm.api_call('conversations.history', channel=channel_id, limit=limit, cursor=cursor)

		if history['ok']:
			view['messages'] = list(reversed(history['messages']))
			view['has_more'] = history['has_more']
			view['next_cursor'] = history['response_metadata']['next_cursor']
		else:
			raise Exception(history.error)

		return view

	def update_view_history(self):
		# this gets history for the channel currently in view, so we don't need any args
		# TODO just setup self.view in get_channel and call this

		channel = self.view['channel']['id']
		limit = self.MSG_HISTORY_LIMIT
		cursor = self.view['next_cursor']
		history = self.comm.api_call('conversations.history', channel=channel, limit=limit, cursor=cursor)

		if history['ok']:
			self.view['messages'] = list(reversed(history['messages'])) + self.view['messages']
			self.view['has_more'] = history['has_more']
			self.view['next_cursor'] = history['response_metadata']['next_cursor']
		else:
			raise Exception(history.error)

	def updateMessages(self, msg):
		message = json.loads(msg)
		msg_type = message.get('type', 'none')
		# TODO handle when you send a message
		if msg_type == 'message':
			# TODO update channels not currently in the view
			if message['channel'] == self.view['channel']['id']:
				msgs = self.view['messages']
				msgs.append(message)
				self.view['messages'] = msgs
				self.update_model_view()

	def get_channel_by_id(self, chan_id):
		return [ch for ch in self.boot['channel_list'] if ch['id'] == chan_id][0]

	def send_msg(self, text):
		# format and pass it along to the comm to send it through the WS
		# tbh, it's probably better to send a message through the API...
		# but I didn't work on making callbacks fast to NOT use this soooo ¯\_(ツ)_/¯
		msg = {
			'type': 'message',
			'channel': self.view['channel']['id'],
			'user': self.boot['self']['id'],
			'text': text
		}
		self.comm.send_message(json.dumps(msg))
		# TODO update read marker for that channel

	def store_model(self):
		# build our local model: rtm data (boot), current view (view) and api token (api_token)
		model = {
			'boot': self.boot,
			'view': self.view
		}

		# create a Slark directory: in the future this will be created with install
		if not os.path.exists(store_dir):
			os.makedirs(store_dir)


		# check the file is there, create it if it isn't
		try:
			file = open(store_path, 'wb')
		except FileNotFoundError:
			file = open(store_path, 'wb+')

		# now pickle to the file
		pickle.dump(model, file)
		file.close()

	def update_model_view(self):
		# get the current model, and rebuild with a new view
		try:
			with open(store_path, 'rb') as store:
				model = pickle.load(store)
				boot = model['boot']
				model = {
					'boot': boot,
					'view': self.view
				}

		except IOError:
			raise Exception('reading model failed :(')

		# store it!
		try:
			with open(store_path, 'wb') as file:
				pickle.dump(model, file)

		except IOError:
			raise Exception('updating model failed :(')



import os
import json
from lib.slark.slark_comm import SlarkComm
from lib.slark.slark_client import SlarkClient

# i stole this from a client, this should be gotten through the oauth flow


class Slark:
	def __init__(self):
		self.api_token = os.environ["SLACK_API_TOKEN"]
		self.MSG_HISTORY_LIMIT = 30
		self.client = SlarkClient()				# prep all the methods for handling the data we get
		self.comm = SlarkComm(self.api_token)	# setup a WS & API client
		self.boot = self.rtm_start()			# get all the boot data from an rtm.start call
		self.view = self.get_channel()			# the current channel in view, and its history. TODO have this accept a stored "last channel"

	def rtm_start(self):
		reply = self.comm.api_call('rtm.start', simple_latest=True)

		if reply['ok']:
			self.comm.set_ws_url(reply['url'])
			self.comm.ws_connect()
		else:
			raise Exception(reply.error)

		return self.client.setup_boot(reply)

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


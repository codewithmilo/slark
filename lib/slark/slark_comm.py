import sys
import json
import urwid
import platform
import requests
import websocket
import threading

VERSION = "0.1"

class SlarkComm:
	def __init__(self, api_token):
		self.token = api_token
		self.ua = self.user_agent()
		self.ws_url = ''
		self.ws = None
		# oh yeah. ty urwid
		self.signals = urwid.Signals()
		self.signals.register(self.signals.__class__, ['on-msg'])

	def set_ws_url(self, url):
		self.ws_url = url

	def ws_connect(self):
		self.ws = websocket.WebSocketApp(self.ws_url,
			on_message=self.on_message,
			on_error=self.on_error,
			on_close=self.on_close,
			on_open=self.on_open)

		thread = threading.Thread(target=self.ws_run, daemon=True)
		thread.start()

	def ws_run(self):
		try:
			self.ws.run_forever()
		except WebSocketConnectionClosedException as e:
			raise Exception(e)

	def send_message(self, msg):
		# send an arbitrary WS message! yahoo! the caller needs to format it
		self.ws.send(msg)

	def on_message(self, ws, message):
		# receive an arbitrary WS message! yahoo! update the UI!
		self.signals.emit(self.signals, 'on-msg', message)

	def on_error(self, ws, error):
		pass

	def on_close(self, ws):
		pass

	def on_open(self, ws):
		pass


	def api_call(self, method, **args):

		# use rtm_payload.json instead so we don't get ratelimited, but get a new WS url :D
		connect_only = method == 'rtm.start'
		if method == 'rtm.start' and connect_only:
			method = 'rtm.connect'

		post_data = args or {}
		url = 'https://slack.com/api/{0}'.format(method)
		post_data['token'] = self.token
		headers = {'user-agent': self.ua}

		req = requests.post(url,
			headers=headers,
			data=post_data)

		if req.status_code != 200:
			raise Exception(req)

		reply = req.json()
		if connect_only:
			ws_url = reply['url']
			reply = json.load(open('rtm_payload.json'))
			reply['url'] = ws_url
		return reply

	def user_agent(self):
		return "Slark/{0} Python/{v.major}.{v.minor}.{v.micro} {1}/{2}".format(VERSION,
			platform.system(), platform.release(),
			v=sys.version_info)
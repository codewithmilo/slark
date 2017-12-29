import requests

import sys
import platform
import json

VERSION = "0.1"

class SlarkComm:
	def __init__(self, api_token):
		self.token = api_token
		self.ua = self.user_agent()
		self.ws_url = ''

	def set_ws_url(self, url):
		self.ws_url = url

	def api_call(self, method, **args):

		# use rtm_payload.json instead so we don't get ratelimited :D
		if method == 'rtm.start':
			return json.load(open('rtm_payload.json'))

		post_data = args or {}
		url = 'https://slack.com/api/{0}'.format(method)
		post_data['token'] = self.token
		headers = {'user-agent': self.ua}

		req = requests.post(url,
			headers=headers,
			data=post_data)

		if req.status_code != 200:
			raise Exception(req)

		return req.json()

	def user_agent(self):
		return "Slark/{0} Python/{v.major}.{v.minor}.{v.micro} {1}/{2}".format(VERSION,
			platform.system(), platform.release(),
			v=sys.version_info)
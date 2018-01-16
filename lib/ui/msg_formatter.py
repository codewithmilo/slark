import re
import html
import urwid
from datetime import datetime

#
# the messages themselves are in this class.
# this allows you to select them and open them for message details
#

class MsgMeta(urwid.Button):
	def __init__(self, label):
		super().__init__(label)
		# hack here to hide the cursor: set the cursor position to one past the text length,
		# thanks to https://stackoverflow.com/questions/34633447/urwid-make-cursor-invisible
		length = len(label[1]) + 1
		self._w = urwid.AttrMap(urwid.SelectableIcon(label, length), None, 'metadata')


#
# call format() method to return a urwid-formatted message item.
# all different message types are handled in this class
#

class MsgFormatter():
	def __init__(self, slark):
		self.slark = slark
		self.mentions_re = '<@([UWB][A-Z\d]+)>'

	def format(self, msg):

		if not msg.get('subtype'):
			# user message
			return self.format_user_msg(msg)
		elif msg.get('subtype') == 'bot_message':
			# bot message
			return self.format_bot_msg(msg)
		else:
			# do this until we get all the types
			return self.format_rando_msg(msg)

	# replace mentions in the code with usernames
	def mentions_repl(self, matchob):
			uid = matchob.group(1)
			id_type = 'bot' if uid[0:1] == 'B' else 'user'

			if id_type == 'user':
				names = self.slark.boot['user_list']
				name = '@' + names.get(uid, 'someone')
			elif id_type == 'bot':
				names = self.slark.boot['bot_list']
				if names.get(uid):
					name = '@' + names.get(uid)
				else:
					name = 'ROBOT SERIAL NO. ' + uid
			return name

	def time_str_format(self, ts):
		dt = datetime.fromtimestamp(float(ts))
		time = dt.strftime('%H:%M')
		return time

	def msg_text_format(self, msg):
		text = msg['text'] if msg['text'] is not None else ''
		text = re.sub(self.mentions_re, self.mentions_repl, text)

		attachments = msg.get('attachments', '')
		if len(attachments):
			text = text if len(text) else ''
			full_text = [(None, text)]
			for att in attachments:
				div = (None, '\n|  ')
				title_yes = len(att.get('title', '')) > 0
				title = att.get('title', '') if title_yes else ''
				title = html.unescape(html.unescape(title)) # this is...dumb
				w_title = ('att-title', title)

				txt_yes = len(att.get('text', '')) > 0
				txt = '\n|  ' + att.get('text', att.get('fallback', '')) if txt_yes else ''

				# TODO use the links and the pics

				if title_yes:
					full_text = full_text + [div, w_title, (None, txt)]
				else:
					full_text = full_text + [w_title, (None, txt)]

			return urwid.Text(full_text)
		else:
			return urwid.Text(text)

	def format_user_msg(self, msg):
		author = self.slark.boot['user_list'][msg['user']]
		time = self.time_str_format(msg['ts'])
		message = self.msg_text_format(msg)
		metadata = MsgMeta(('metadata', author+' @ '+time))
		return [urwid.Divider(), metadata, message]

	def format_bot_msg(self, msg):
		author = self.slark.boot['bot_list'][msg['bot_id']]
		time = self.time_str_format(msg['ts'])
		message = self.msg_text_format(msg)
		metadata = MsgMeta(('metadata', author+' @ '+time))
		return [urwid.Divider(), metadata, message]

	def format_rando_msg(self, msg):
		user = msg.get('user', 'someone')
		author = self.slark.boot['user_list'].get(user, 'someone')
		time = self.time_str_format(msg['ts'])
		message = self.msg_text_format(msg)
		metadata = MsgMeta(('metadata', author+' @ '+time))
		return [urwid.Divider(), metadata, message]



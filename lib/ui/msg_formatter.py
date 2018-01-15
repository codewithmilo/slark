import re
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

	def format(self, msg):

		if msg['type'] == 'message' and not msg.get('subtype'):
			# user message
			return self.format_user_msg(msg)

	# replace mentions in the code with usernames
	def mentions_repl(self, matchob):
			uid = matchob.group(1)
			name = self.slark.boot['user_list'].get(uid, 'someone')
			return '@'+name

	def format_user_msg(self, msg):
		author = self.slark.boot['user_list'][msg['user']]
		ts = datetime.fromtimestamp(float(msg['ts']))
		time = ts.strftime('%H:%M')
		text = msg.get('text', '')
		text = re.sub('<@(U[A-Z\d]+)>', self.mentions_repl, text)
		message = urwid.Text(text)
		metadata = MsgMeta(('metadata', author+' @ '+time))
		return [urwid.Divider(), metadata, message]


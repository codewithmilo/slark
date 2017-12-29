import urwid
import datetime
import re
from lib.ui.msg_input import MsgInput
from lib.ui.msg_pane import MsgPane

class Panes:
	def __init__(self, slark):
		self.slark = slark
		self.msg = self.msg_pane()
		self.ch = self.channel_pane()

	def channel_pane(self):
		head_title = urwid.Text(('banner', u'\nChannels\n'), align='center')
		head = urwid.AttrMap(head_title, 'streak')

		body = []
		# find the channel in view and get its position in this list
		focus_position = 0
		for c in self.slark.boot['channel_list_visible']:
			ch_item = ChannelItem(c['name'], self.switchChannels, c['id'])
			ch_item = urwid.AttrMap(ch_item, None, focus_map='focused')
			body = body + [urwid.Divider(), ch_item]
			if c['id'] == self.slark.view['channel']['id']:
				focus_position = len(body) - 1

		ch_list = urwid.ListBox(body)
		ch_list.set_focus(focus_position)

		return urwid.Frame(ch_list, head)

	def msg_pane(self):
		# header is the name of the current channel
		head_title = urwid.Text(('banner', '\n'+self.slark.view['channel']['name']+'\n'), align='center')
		header = urwid.AttrMap(head_title, 'streak')

		msg_rows = self.build_msg_rows(self.slark.view['messages'])
		msg_list = MsgPane(msg_rows)
		self.setup_msg_pane_hooks(msg_list)

		# set the focus to the last msg row, and align it with the bottom
		msg_list.set_focus(len(msg_rows)-1)

		# footer is text input, for sending the messages!
		msg_input = MsgInput()
		msg_input = urwid.AttrMap(msg_input, 'input')
		input_div = urwid.AttrMap(urwid.Divider(), 'input')

		# connect keyboard navigation signals to change focus
		urwid.connect_signal(msg_input.original_widget, 'move-focus', self.navigate)
		urwid.connect_signal(msg_input.original_widget, 'send-msg', self.update_msg_pane)
		msg_box = urwid.Pile([urwid.Divider(), input_div, msg_input, input_div])

		return urwid.Frame(msg_list, header, msg_box, focus_part='footer')

	def build_msg_rows(self, messages):

		def mentions_repl(matchob):
			uid = matchob.group(1)
			name = self.slark.boot['user_list'].get(uid, 'someone')
			return '@'+name

		msg_rows = []
		for msg in messages:
			author = self.slark.boot['user_list'][msg['user']]
			ts = datetime.datetime.fromtimestamp(float(msg["ts"]))
			time = ts.strftime('%H:%M')
			text = msg.get('text', '')
			text = re.sub('<@(U[A-Z\d]+)>', mentions_repl, text)
			message = urwid.Text(text)
			metadata = urwid.Text(('metadata', author+' @ '+time))
			msg_rows = msg_rows + [urwid.Divider(), metadata, message]
		return msg_rows

	def setup_msg_pane_hooks(self, msg_pane):
		urwid.connect_signal(msg_pane, 'move-focus', self.navigate)
		urwid.connect_signal(msg_pane, 'focus-and-type', self.navigateAndType)
		urwid.connect_signal(msg_pane, 'more-history', self.fetchMoreHistory)

	def switchChannels(self, button, new_chan_id):
		# update slark.view, then update the header and msg pane
		self.slark.view = self.slark.get_channel(new_chan_id)
		new_name = self.slark.view['channel']['name']
		new_msgs = self.build_msg_rows(self.slark.view['messages'])

		header = self.msg.contents['header'][0]
		header.original_widget.set_text(u'\n'+new_name+'\n')

		msg_pane = MsgPane(new_msgs)
		self.setup_msg_pane_hooks(msg_pane)

		self.msg.contents['body'] = (msg_pane, None)
		self.msg.contents['body'][0].set_focus(len(new_msgs)-1)
		self.msg.set_focus('body')

	def build(self):
		return (self.ch, self.msg)

	def navigate(self, key):
		if key == 'up':
			self.msg.set_focus('body')
		if key == 'down':
			self.msg.set_focus('footer')

	def navigateAndType(self, key):
		self.msg.set_focus('footer')
		self.msg.focus.focus.original_widget.insert_text(key)

	def fetchMoreHistory(self):
		self.slark.update_view_history()
		# now, self.slark.view is updated with the older messages. re-render the list, i guess?
		new_msgs = self.build_msg_rows(self.slark.view['messages'])

		# how do we know how many messages were just added? well, use the MSG_HISTORY_LIMIT * 3
		# and that's probably accurate. at some point, we should be smarter though
		focus_pos = self.slark.MSG_HISTORY_LIMIT * 3 - 1

		self.msg.contents['body'][0].body = urwid.SimpleFocusListWalker(new_msgs)
		self.msg.contents['body'][0].set_focus(focus_pos)
		self.msg.contents['body'][0].set_focus_valign('top')

	def update_msg_pane(self, text):
		body = self.msg.contents['body'][0].body

		# current time and user for metadata!
		ts = datetime.datetime.now().strftime('%H:%M')
		message = urwid.Text(text)
		author = self.slark.boot['self']['name']
		metadata = urwid.Text(('metadata', author+' @ '+ts))

		body = body + [urwid.Divider(), metadata, message]
		msg_rows = len(body)

		self.msg.contents['body'][0].body = urwid.SimpleFocusListWalker(body)
		self.msg.contents['body'][0].set_focus(msg_rows-1)
		self.msg.set_focus('body')

class ChannelItem(urwid.Button):
	def __init__(self, label, on_press, user_data):
		super(ChannelItem, self).__init__('')
		urwid.connect_signal(self, 'click', on_press, user_data)
		self._w = urwid.AttrMap(urwid.SelectableIcon(label, 0), None, 'focused')

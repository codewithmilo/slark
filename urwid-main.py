import urwid
import json
import datetime

channels = u'general random cats feat-slark'.split()

msg_json = json.load(open('messages.json'))
messages = msg_json["messages"]


def channel_list(channels):
	head_title = urwid.Text(('banner', u'\nChannels\n'), align='center')
	# head = urwid.Filler(head_title)
	# head = urwid.BoxAdapter(head, 3)

	# head = urwid.AttrMap(head, 'banner')
	head = urwid.AttrMap(head_title, 'streak')

	# head = urwid.Text(('banner', u'Channels'))
	# head = urwid.AttrMap(head, 'banner')

	# print head

	body = []
	for c in channels:
		button = urwid.Button(c)
		urwid.connect_signal(button, 'click', channel_chosen, c)
		body.append(urwid.AttrMap(button, None, focus_map='focused'))

	return urwid.Frame(urwid.ListBox(body), head)

def msg_pane():
	head_title = urwid.Text(('banner', u'\n#general\n'), align='center')
	head = urwid.AttrMap(head_title, 'streak')

	msg_rows = []
	for msg in reversed(messages):
		# author = urwid.Text(('author', msg["user"]), align='center')
		author = msg["user"]

		ts = datetime.datetime.fromtimestamp(float(msg["ts"]))
		time = ts.strftime('%H:%M')
		# timestamp = urwid.Text(('msg ts', time))

		message = urwid.Text(msg["text"])

		# author_width = author.pack()[0]

		# metadata = urwid.GridFlow([author, timestamp], author_width+2, 1, 0, 'left')
		metadata = urwid.Text(('metadata', author+' @ '+time))
		# msg_row = urwid.Pile([('pack', metadata), message], 1)
		# msg_row = urwid.Frame(message, urwid.Text(author+'\t'+time))

		msg_rows.append(urwid.Divider())
		msg_rows.append(metadata)
		msg_rows.append(message)

	all_messages = urwid.ListBox(msg_rows)

	return urwid.Frame(all_messages, head)

def channel_chosen(button, channel):
    header = msg.focus
    title = header.original_widget
    title.set_text(u'\n#'+channel+'\n')

def exit_on_q(key):
	if key == 'q':
		raise urwid.ExitMainLoop()

palette = [
	('focused', 'light green', 'black'),
	('banner', 'white', 'black'),
	('streak', 'white', 'black'),
	('metadata', 'black', 'light gray'),]

ch = channel_list(channels)
msg = msg_pane()

main = urwid.Columns([('weight', 1, ch), ('weight', 3, msg)], 1)
loop = urwid.MainLoop(main, palette, unhandled_input=exit_on_q)

loop.run()
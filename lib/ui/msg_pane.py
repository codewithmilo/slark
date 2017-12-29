import urwid

class MsgPane(urwid.ListBox):
	def __init__(self, body):
		b = urwid.SimpleFocusListWalker(body)
		return super(MsgPane, self).__init__(b)

	signals = ['move-focus', 'focus-and-type', 'more-history']

	def keypress(self, size, key):
		if key == 'down':
			# if we are at the bottom, tell the frame to move to msg input
			visible = self.ends_visible(size)
			if len(visible) and visible[0] == 'bottom':
				urwid.emit_signal(self, 'move-focus', key)
		if key == 'up':
			# check if we are at the top of history. if we are, send the signal to add some more
			visible = self.ends_visible(size)
			if len(visible) and visible[0] == 'top':
				urwid.emit_signal(self, 'more-history')
		if key not in ('up', 'down', 'left', 'page down', 'page up', 'right', 'esc'):
			urwid.emit_signal(self, 'focus-and-type', key)

		super(MsgPane, self).keypress(size, key)
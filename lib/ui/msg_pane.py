import urwid

# the full message pane, which is just a big list of messages.
# mostly created to handle keyboard nav

class MsgPane(urwid.ListBox):
	def __init__(self, body):
		b = urwid.SimpleFocusListWalker(body)
		return super(MsgPane, self).__init__(b)

	signals = ['move-focus', 'focus-and-type', 'more-history', 'mark-read']

	def keypress(self, size, key):
		if key == 'down':
			# if we are at the bottom, tell the frame to move to msg input
			# subtract 2 because the last item is just text; not a selectable
			visible = self.ends_visible(size)

			full_len = len(self.body) - 2
			if self.focus_position == full_len and len(visible) and visible[0] == 'bottom':
				urwid.emit_signal(self, 'move-focus', key)
				return

		if key == 'up':
			# check if we are at the top of history. if we are, send the signal to add some more
			visible = self.ends_visible(size)
			if len(visible) and visible[0] == 'top':
				urwid.emit_signal(self, 'more-history')
				return

		if key == 'enter':
			# hit enter in the message list to mark the channel unread
			urwid.emit_signal(self, 'mark-read')
			return

		if key not in ('up', 'down', 'left', 'page down', 'page up', 'right', 'esc'):
			urwid.emit_signal(self, 'focus-and-type', key)

		super(MsgPane, self).keypress(size, key)
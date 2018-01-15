import urwid

class MsgInput(urwid.Edit):

	signals = ['move-focus', 'send-msg']

	def submitMsg(self):
		urwid.emit_signal(self, 'send-msg', self.edit_text)
		self.set_edit_text('')

	def keypress(self, size, key):

		if key == 'enter':
			# send a message
			self.submitMsg()
		if key == 'up' and self.get_cursor_coords(size)[1] == 0:
			# if we are at the top of the input, tell the frame to move focus
			return urwid.emit_signal(self, 'move-focus', key)
		if key == 'esc':
			raise urwid.ExitMainLoop()

		# send through to the Edit if it isn't anything special
		super(MsgInput, self).keypress(size, key)
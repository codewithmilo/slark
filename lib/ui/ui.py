import urwid
import json
from lib.ui.panes import Panes

def load_ui(slark):

	palette = [
		('focused', 'standout', 'light gray'),
		('banner', 'white', 'black'),
		('streak', 'white', 'black'),
		('metadata', 'black', 'light gray'),
		('input', 'white', 'dark gray')]

	main_pane = Panes(slark)
	main = MainUI([
		('weight', 1, main_pane.ch),
		('weight', 3, main_pane.msg)])
	loop = urwid.MainLoop(main, palette)

	loop.run()

class MainUI(urwid.Columns):
	def keypress(self, size, key):
		if key == 'left' and self.focus_position == 1:
			self.set_focus_column(0)
		if key == 'esc':
			raise urwid.ExitMainLoop()
		super(MainUI, self).keypress(size, key)

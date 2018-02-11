import json
import urwid
from lib.ui.panes import Panes

def load_ui(slark):

	palette = [
		('focused', 'standout', 'light gray'),
		('banner', 'white', 'black'),
		('streak', 'white', 'black'),
		('metadata', 'black', 'light gray'),
		('input', 'white', 'dark gray'),
		('unread', 'bold', ''),
		('att-title', 'underline', '')]

	main_pane = Panes(slark)
	main = MainUI([
		('weight', 1, main_pane.ch),
		('weight', 3, main_pane.msg)], 1)
	loop = urwid.MainLoop(main, palette, handle_mouse=False)
	urwid.connect_signal(loop.widget.contents[1][0], 'redraw-msg', loop.draw_screen)
	loop.run()

class MainUI(urwid.Columns):
	def keypress(self, size, key):
		if key == 'left' and self.focus_position == 1:
			self.set_focus_column(0)
		if key == 'esc':
			raise urwid.ExitMainLoop()
		super(MainUI, self).keypress(size, key)

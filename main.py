import argparse
from lib.ui.ui import load_ui
from lib.slark.slark import Slark

parser = argparse.ArgumentParser(description='Run Slack through slark!')
parser.add_argument(
	'-w', '--websocket',
	action='store_true',
	help='Open the websocket only, without a UI',
	dest='ws')

args = parser.parse_args()

slark = Slark(args)

if args.ws == True:
	# TODO make this a nice urwid UI and catch keypresses to quit
	slark.comm.ws_connect()
else:
	load_ui(slark)

import os
import argparse
from appdirs import AppDirs
from lib.ui.ui import load_ui
from lib.slark.slark import Slark

parser = argparse.ArgumentParser(description='Run Slack through slark!')
parser.add_argument(
	'-w', '--websocket',
	action='store_true',
	help='Open the websocket only, without a UI',
	dest='ws')
parser.add_argument(
	'-c', '--client-only',
	action='store_true',
	help='Open the client only, without a websocket connection',
	dest='co')
parser.add_argument(
	'-d', '--delete',
	action='store_true',
	help='Delete the locally stored data file',
	dest='de')

args = parser.parse_args()

if args.de:
	# keep this in sync with the location in slark.py
	dirs = AppDirs('Slark', 'Milo')
	store_dir = dirs.user_data_dir
	store_path = store_dir + '/slark_model.pickle'
	try:
		os.remove(store_path)
	except FileNotFoundError:
		print("Looks like there isn't a locally stored data file!")
	exit()


slark = Slark(args)

if args.ws:
	# TODO make this a nice urwid UI and catch keypresses to quit
	slark.comm.ws_connect()
else:
	load_ui(slark)

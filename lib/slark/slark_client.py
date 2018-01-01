
class SlarkClient():

	def setup_boot(self, data):
		#
		# the Slark 'boot' property has all the shit we will need. Populate it now!
		#

		boot = data

		# mapping of user_id => user name, so it's easy to display
		user_list = {}
		# all the channels in one list, with minimal data
		channel_list = []
		# channel list without archived or non-member channels, and sorted
		channel_list_visible = []

		# map the users first, to use it later with DMs
		for u in data['users']:
			# lookup display name in the users list
			if u['id'] == 'USLACKBOT':
				name = 'slackbot'
			elif u['id'] == data['self']['id']:
				name = data['self']['name']
			else:
				if len(u['profile']['display_name']) > 0:
					name = u['profile']['display_name']
				else:
					name = u['profile']['real_name']

			user_list[u['id']] = name

		boot['user_list'] = user_list

		# now do the channels
		for ch in data['channels']:
			chan = {}
			if ch['is_archived'] == True:
				continue

			chan['name'] = u'#'+ch['name']
			chan['id'] = ch['id']
			chan['is_private'] = ch['is_private']
			chan['latest'] = ch.get('latest', '0')
			chan['last_read'] = ch.get('last_read', '0')
			chan['members'] = len(ch.get('members', '0'))
			chan['priority'] = ch.get('priority', '0')
			chan['unreads'] = ch.get('unread_count', '0')
			chan['is_member'] = ch['is_member']
			chan['is_archived'] = ch['is_archived']

			# take down the general channel for reference later
			if ch['is_general'] == True:
				boot['general'] = chan

			channel_list.append(chan)

		for g in data['groups']:
			group = {}
			group['id'] = g['id']
			group['is_private'] = True
			group['latest'] = g.get('latest', '0')
			group['last_read'] = g.get('last_read', '0')
			group['members'] = len(g.get('members', '0'))
			group['priority'] = g.get('priority', '0')
			group['unreads'] = g.get('unread_count', '0')
			group['is_member'] = True
			group['is_archived'] = g['is_archived']

			if g['is_mpim']:
				# TODO use display names here: lookup by members
				name = g['name'][5:-2]
				name = name.replace('--', ', ')
			else:
				name = u'*'+g['name']
			group['name'] = name

			channel_list.append(group)

		for i in data['ims']:
			im = {}
			im['id'] = i['id']
			im['name'] = user_list[i['user']]
			if im['name'] == data['self']['name']:
				im['name'] = im['name'] + ' (you)'
			im['is_private'] = True
			im['latest'] = i.get('latest', '0')
			im['last_read'] = i.get('last_read', '0')
			im['members'] = 2
			im['priority'] = i.get('priority', '0')
			im['unreads'] = i.get('unread_count', '0')
			im['is_member'] = True
			im['is_archived'] = False



			channel_list.append(im)

		boot['channel_list'] = channel_list

		# filter out archived channels and those you aren't a member of
		channel_list_visible = filter(lambda c: c['is_member'] == True and c['is_archived'] == False, channel_list)

		# now sort based on priority if the pref says so
		if data['self']['prefs']['channel_sort'] == 'priority':
			channel_list_visible = sorted(channel_list_visible, key=lambda k: k['priority'], reverse=True)

		boot['channel_list_visible'] = channel_list_visible

		return boot

def update_user_setting_filters(data, key, user_setting):
	timespan_map = {
		'1 week': 'week',
		'1 month': 'month',
		'3 months': 'quarter',
		'6 months': '6 months',
		'1 year': 'year',
	}

	period_map = {
		'Previous': 'last',
		'Next': 'next'
	}

	if data.get(key):
		update = False
		if isinstance(data.get(key), dict):
			filters = data.get(key).get('filters')
			for f in filters:
				if f[2] == 'Next' or f[2] == 'Previous':
					update = True
					f[3] = period_map[f[2]] + ' ' + timespan_map[f[3]]
					f[2] = 'Timespan'

			if update:
				data[key]['filters'] = filters
				update_user_settings(user_setting['doctype'], json.dumps(data), for_update=True)
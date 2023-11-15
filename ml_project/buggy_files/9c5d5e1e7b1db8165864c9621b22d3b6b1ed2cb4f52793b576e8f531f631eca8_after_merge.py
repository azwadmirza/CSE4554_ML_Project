def get_unique_scan_id():
	scan_id = ''
	while scan_id == '':
		rand = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
		count, context = current_app.elastic.get_host_by_scan_id(rand)
		if count == 0:
			scan_id = rand
	return scan_id
def submit():
	status_code = None
	response_body = None
	data = request.get_json()
	newhost = {}
	newhost = json.loads(data)
	newhost['ctime'] = dt.now(tz.utc)
	if newhost['scan_reason'] == 'requested':
		mark_scan_completed(newhost['ip'], newhost['scan_id'])

	try:
		nmap = NmapParser.parse(newhost['xml_data'])
		# If there's more or less than 1 host in the xml data, reject it (for now)
		if nmap.hosts_total != 1:
			status_code = 400
			response_body = json.dumps({"status": status_code, "message": "XML had too many hosts in it", "retry": False})

		# If it's not an acceptable target, tell the agent it's out of scope
		elif not current_app.ScopeManager.isAcceptableTarget(nmap.hosts[0].address):
			status_code = 400
			response_body = json.dumps({"status": status_code, "message": "Out of scope: " + nmap.hosts[0].address, "retry": False})

		# If there's no further processing to do, store the host and prepare the response
		elif not newhost["is_up"] or (newhost["is_up"] and newhost["port_count"] == 0):
			current_app.elastic.new_result(newhost)
			status_code = 200
			response_body = json.dumps({"status": status_code, "message": "Received: " + newhost['ip']})
	except NmapParserException:
		status_code = 400
		response_body = json.dumps({"status": status_code, "message": "Invalid nmap xml data provided", "retry": False})

	# If status_code and response_body have been set by this point, return a response.
	if status_code and response_body:
		response = Response(response=response_body, status=status_code, content_type=json_content)
		return response

	if newhost['scan_start'] and newhost['scan_stop']:
		elapsed = dateutil.parser.parse(newhost['scan_stop']) - dateutil.parser.parse(newhost['scan_start'])
		newhost['elapsed'] = elapsed.seconds

	newhost['ip'] = nmap.hosts[0].address
	if len(nmap.hosts[0].hostnames) > 0:
		newhost['hostname'] = nmap.hosts[0].hostnames[0]

	tmpports = []
	newhost['ports'] = []

	for port in nmap.hosts[0].get_open_ports():
		tmpports.append(str(port[0]))
		srv = nmap.hosts[0].get_service(port[0], port[1])
		portinfo = srv.get_dict()
		portinfo['service'] = srv.service_dict
		portinfo['scripts'] = []
		for script in srv.scripts_results:
			scriptsave = {"id": script['id'], "output": script["output"]}
			portinfo['scripts'].append(scriptsave)
			if script['id'] == "ssl-cert":
				portinfo['ssl'] = parse_ssl_data(script)

		newhost['ports'].append(portinfo)

	newhost['port_str'] = ', '.join(tmpports)

	if 'screenshots' in newhost and newhost['screenshots']:
		newhost['screenshots'], newhost['num_screenshots'] = process_screenshots(newhost['screenshots'])

	if len(newhost['ports']) == 0:
		status_code = 200
		response_body = json.dumps({"status": status_code, "message": "Expected open ports but didn't find any for %s" % newhost['ip']})
	elif len(newhost['ports']) > 500:
		status_code = 200
		response_body = json.dumps({"status": status_code, "message": "More than 500 ports found, throwing data out"})
	else:
		status_code = 200
		current_app.elastic.new_result(newhost)
		response_body = json.dumps({"status": status_code, "message": "Received %s ports for %s" % (len(newhost['ports']), newhost['ip'])})

	response = Response(response=response_body, status=status_code, content_type=json_content)
	return response
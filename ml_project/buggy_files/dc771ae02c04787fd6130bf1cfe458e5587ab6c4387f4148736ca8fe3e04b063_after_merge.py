def scan(target_data=None):

	if not validate_target(target_data["target"]):
		return ERR["INVALIDTARGET"]

	result = {}

	# If agent authentication is required, this agent id has to match a server side agent id
	# If it's not required and an agent_id is set, we'll use that in scan data
	# If it's not required and an agent_id is not set, we'll consider it an anonymous scan.
	if config.agent_id:
		result['agent'] = config.agent_id
	else:
		result['agent'] = "anonymous"
	result["agent_version"] = config.NATLAS_VERSION

	target = target_data["target"]
	result['ip'] = target
	result['scan_reason'] = target_data['scan_reason']
	result['tags'] = target_data['tags']
	scan_id = target_data["scan_id"]
	result['scan_id'] = scan_id
	agentConfig = target_data["agent_config"]
	result['scan_start'] = datetime.now(timezone.utc).isoformat()

	command = ["nmap", "-oA", "data/natlas."+scan_id, "--servicedb", "./natlas-services"]
	if agentConfig["versionDetection"]:
		command.append("-sV")
	if agentConfig["osDetection"]:
		command.append("-O")
	if agentConfig["enableScripts"] and agentConfig["scripts"]:
		command.append("--script")
		command.append(agentConfig["scripts"])
	if agentConfig["scriptTimeout"]:
		command.append("--script-timeout")
		command.append(str(agentConfig["scriptTimeout"]))
	if agentConfig["hostTimeout"]:
		command.append("--host-timeout")
		command.append(str(agentConfig["hostTimeout"]))
	if agentConfig["osScanLimit"]:
		command.append("--osscan-limit")
	if agentConfig["noPing"]:
		command.append("-Pn")
	if agentConfig["onlyOpens"]:
		command.append("--open")

	command.append(target_data["target"])

	TIMEDOUT = False
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	try:
		out, err = process.communicate(timeout=int(agentConfig["scanTimeout"]))
	except:
		try:
			TIMEDOUT = True
			print_err("Scan %s timed out" % scan_id)
			process.kill()
		except:
			pass

	if TIMEDOUT:
		result['is_up'] = False
		result['port_count'] = 0
		result['scan_stop'] = datetime.now(timezone.utc).isoformat()
		result['timed_out'] = True
		cleanup_files(scan_id)
		print_info("Submitting scan timeout notice for %s" % result['ip'])
		response = backoff_request(giveup=True, endpoint="/api/submit", reqType="POST", postData=json.dumps(result))
		return
	else:
		print_info("Scan %s Complete" % scan_id)

	for ext in 'nmap', 'gnmap', 'xml':
		try:
			result[ext+"_data"] = open("data/natlas."+scan_id+"."+ext).read()
		except:
			print_err("Couldn't read natlas.%s.%s" % (scan_id, ext))
			return ERR["DATANOTFOUND"]

	nmap_report = NmapParser.parse(result['xml_data'])

	if nmap_report.hosts_total < 1:
		print_err("No hosts found in scan data")
		return "[!] No hosts found in scan data"
	elif nmap_report.hosts_total > 1:
		print_err("Too many hosts found in scan data")
		return "[!] Too many hosts found in scan data"
	elif nmap_report.hosts_down == 1:
		# host is down
		result['is_up'] = False
		result['port_count'] = 0
		result['scan_stop'] = datetime.now(timezone.utc).isoformat()
		cleanup_files(scan_id)
		print_info("Submitting host down notice for %s" % (result['ip']))
		response = backoff_request(giveup=True, endpoint="/api/submit", reqType="POST", postData=json.dumps(result))
		return
	elif nmap_report.hosts_up == 1 and len(nmap_report.hosts) == 0:
		# host is up but no reportable ports were found
		result['is_up'] = True
		result['port_count'] = 0
		result['scan_stop'] = datetime.now(timezone.utc).isoformat()
		cleanup_files(scan_id)
		print_info("Submitting %s ports for %s" % (result['port_count'], result['ip']))
		response = backoff_request(giveup=True, endpoint="/api/submit", reqType="POST", postData=json.dumps(result))
		return
	else:
		# host is up and reportable ports were found
		result['is_up'] = nmap_report.hosts[0].is_up()
		result['port_count'] = len(nmap_report.hosts[0].get_ports())
	result['screenshots'] = []

	if target_data["agent_config"]["webScreenshots"] and shutil.which("aquatone") is not None:
		targetServices=[]
		if "80/tcp" in result['nmap_data']:
			targetServices.append("http")
		if "443/tcp" in result['nmap_data']:
			targetServices.append("https")
		if len(targetServices) > 0:
			print_info("Attempting to take %s screenshot(s) for %s" % (', '.join(targetServices).upper(),result['ip']))
			screenshotutils.runAquatone(target, scan_id, targetServices)

		serviceMapping = {
			"http": 80,
			"https": 443
		}
		for service in targetServices:
			screenshotPath = "data/aquatone." + scan_id + "/screenshots/" + service + "__" + target.replace('.', '_') + ".png"

			if not os.path.isfile(screenshotPath):
				continue

			result['screenshots'].append({
				"host": target,
				"port": serviceMapping[service],
				"service": service.upper(),
				"data": str(base64.b64encode(open(screenshotPath, 'rb').read()))[2:-1]
			})
			print_info("%s screenshot acquired for %s" % (service.upper(), result['ip']))

	if target_data["agent_config"]["vncScreenshots"] and shutil.which("vncsnapshot") is not None:
		if "5900/tcp" in result['nmap_data']:
			print_info("Attempting to take VNC screenshot for %s" % result['ip'])
			if screenshotutils.runVNCSnapshot(target, scan_id) is True:
				result['screenshots'].append({
					"host": target,
					"port": 5900,
					"service": "VNC",
					"data": str(base64.b64encode(open("data/natlas."+scan_id+".vnc.jpg", 'rb').read()))[2:-1]
				})
				print_info("VNC screenshot acquired for %s" % result['ip'])
			else:
				print_err("Failed to acquire screenshot for %s" % result['ip'])

	# submit result
	result['scan_stop'] = datetime.now(timezone.utc).isoformat()
	cleanup_files(scan_id)
	print_info("Submitting %s ports for %s" % (result['port_count'], result['ip']))
	response = backoff_request(giveup=True, endpoint="/api/submit", reqType="POST", postData=json.dumps(result))
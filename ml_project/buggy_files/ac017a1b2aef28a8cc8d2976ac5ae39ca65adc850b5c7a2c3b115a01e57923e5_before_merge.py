def jobState():
	currentData = printer.get_current_data()
	return jsonify({
		"job": currentData["job"],
		"progress": currentData["progress"],
		"state": currentData["state"]["text"],
		"printingUser": currentData["printingUser"],
	})
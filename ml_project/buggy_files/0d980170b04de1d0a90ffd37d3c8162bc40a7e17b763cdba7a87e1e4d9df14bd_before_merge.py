def get_data():
	return frappe._dict({
		"dashboards": get_dashboards(),
		"charts": get_charts(),
	})
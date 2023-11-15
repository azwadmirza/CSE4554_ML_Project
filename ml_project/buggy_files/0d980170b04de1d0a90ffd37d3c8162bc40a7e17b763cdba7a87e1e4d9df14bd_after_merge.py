def get_data():
	data = frappe._dict({
		"dashboards": [],
		"charts": []
	})
	company = get_company_for_dashboards()
	if company:
		company_doc = frappe.get_doc("Company", company)
		data.dashboards = get_dashboards()
		data.charts = get_charts(company_doc)
	return data
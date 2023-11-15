def get_company_for_dashboards():
	company = get_default_company()
	if not company:
		company_list = frappe.get_list("Company")
		if company_list:
			company = company_list[0].name
	return company
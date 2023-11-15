def get_recipients(service_name, email_field):
	if not frappe.db:
		frappe.connect()

	return split_emails(frappe.db.get_value(service_name, None, email_field))
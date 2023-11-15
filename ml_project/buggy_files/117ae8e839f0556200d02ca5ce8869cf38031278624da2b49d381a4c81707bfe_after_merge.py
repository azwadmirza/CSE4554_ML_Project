def get_recipients(doctype, email_field):
	if not frappe.db:
		frappe.connect()

	return split_emails(frappe.db.get_value(doctype, None, email_field))
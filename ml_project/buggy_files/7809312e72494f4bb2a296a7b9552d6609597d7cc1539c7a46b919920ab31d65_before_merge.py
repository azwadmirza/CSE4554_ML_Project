def send_email(success, service_name, doctype, email_field, error_status=None):
	recipients = get_recipients(service_name, email_field)
	if not recipients:
		frappe.log_error("No Email Recipient found for {0}".format(service_name),
				"{0}: Failed to send backup status email".format(service_name))
		return

	if success:
		if not frappe.db.get_value(doctype, None, "send_email_for_successful_backup"):
			return

		subject = "Backup Upload Successful"
		message = """
<h3>Backup Uploaded Successfully!</h3>
<p>Hi there, this is just to inform you that your backup was successfully uploaded to your {0} bucket. So relax!</p>""".format(service_name)

	else:
		subject = "[Warning] Backup Upload Failed"
		message = """
<h3>Backup Upload Failed!</h3>
<p>Oops, your automated backup to {0} failed.</p>
<p>Error message: {1}</p>
<p>Please contact your system manager for more information.</p>""".format(service_name, error_status)

	frappe.sendmail(recipients=recipients, subject=subject, message=message)
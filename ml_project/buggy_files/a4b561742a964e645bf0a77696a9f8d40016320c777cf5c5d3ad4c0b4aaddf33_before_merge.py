	def on_update(self):
		"""update all email accounts using this domain"""
		for email_account in frappe.get_all("Email Account", filters={"domain": self.name}):
			try:
				email_account = frappe.get_doc("Email Account", email_account.name)
				for attr in ["email_server", "use_imap", "use_ssl", "use_tls", "attachment_limit", "smtp_server", "smtp_port", "use_ssl_for_outgoing", "append_emails_to_sent_folder"]:
					email_account.set(attr, self.get(attr, default=0))
				email_account.save()

			except Exception as e:
				frappe.msgprint(_("Error has occurred in {0}").format(email_account.name), raise_exception=e.__class__)
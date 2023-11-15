	def on_update(self):
		"""update all email accounts using this domain"""
		for email_account in frappe.get_all("Email Account",
		filters={"domain": self.name}):

			try:
				email_account = frappe.get_doc("Email Account",
					email_account.name)
				email_account.set("email_server",self.email_server)
				email_account.set("use_imap",self.use_imap)
				email_account.set("use_ssl",self.use_ssl)
				email_account.set("use_tls",self.use_tls)
				email_account.set("attachment_limit",self.attachment_limit)
				email_account.set("smtp_server",self.smtp_server)
				email_account.set("smtp_port",self.smtp_port)
				email_account.set("incoming_port", self.incoming_port)
				email_account.save()
			except Exception as e:
				frappe.msgprint(email_account.name)
				frappe.throw(e)
				return None
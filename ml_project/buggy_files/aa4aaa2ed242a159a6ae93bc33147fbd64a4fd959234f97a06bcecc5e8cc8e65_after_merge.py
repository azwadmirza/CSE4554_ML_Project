	def make_invoices(self):
		names = []
		mandatory_error_msg = _("Row {idx}: {field} is required to create the Opening {invoice_type} Invoices")
		if not self.company:
			frappe.throw(_("Please select the Company"))

		for row in self.invoices:
			if not row.qty:
				row.qty = 1.0
			if not row.party:
				frappe.throw(mandatory_error_msg.format(
					idx=row.idx,
					field=_("Party"),
					invoice_type=self.invoice_type
				))
			# set party type if not available
			if not row.party_type:
				row.party_type = "Customer" if self.invoice_type == "Sales" else "Supplier"

			if not row.posting_date:
				frappe.throw(mandatory_error_msg.format(
					idx=row.idx,
					field=_("Party"),
					invoice_type=self.invoice_type
				))

			if not row.outstanding_amount:
				frappe.throw(mandatory_error_msg.format(
					idx=row.idx,
					field=_("Outstanding Amount"),
					invoice_type=self.invoice_type
				))

			args = self.get_invoice_dict(row=row)
			if not args:
				continue

			doc = frappe.get_doc(args).insert()
			doc.submit()
			names.append(doc.name)

			if len(self.invoices) > 5:
				frappe.publish_realtime(
					"progress", dict(
						progress=[row.idx, len(self.invoices)],
						title=_('Creating {0}').format(doc.doctype)
					),
					user=frappe.session.user
				)

		return names
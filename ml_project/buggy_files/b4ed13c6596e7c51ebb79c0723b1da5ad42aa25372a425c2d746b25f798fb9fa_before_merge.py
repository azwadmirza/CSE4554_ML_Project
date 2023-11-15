	def on_recurring(self, reference_doc, subscription_doc):
		mcount = month_map[subscription_doc.frequency]
		self.set("delivery_date", get_next_date(reference_doc.delivery_date, mcount,
			cint(subscription_doc.repeat_on_day)))

		for d in self.get("items"):
			reference_delivery_date = frappe.db.get_value("Sales Order Item",
				{"parent": reference_doc.name, "item_code": d.item_code, "idx": d.idx}, "delivery_date")

			d.set("delivery_date",
				get_next_date(reference_delivery_date, mcount, cint(subscription_doc.repeat_on_day)))
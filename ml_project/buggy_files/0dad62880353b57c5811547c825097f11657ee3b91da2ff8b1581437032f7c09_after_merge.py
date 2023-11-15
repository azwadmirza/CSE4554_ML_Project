		def get_item_dict():
			default_uom = frappe.db.get_single_value("Stock Settings", "stock_uom") or _("Nos")
			cost_center = frappe.db.get_value("Company", self.company, "cost_center")
			if not cost_center:
				frappe.throw(
					_("Please set the Default Cost Center in {0} company").format(frappe.bold(self.company))
				)
			rate = flt(row.outstanding_amount) / flt(row.qty)

			return frappe._dict({
				"uom": default_uom,
				"rate": rate or 0.0,
				"qty": row.qty,
				"conversion_factor": 1.0,
				"item_name": row.item_name or "Opening Invoice Item",
				"description": row.item_name or "Opening Invoice Item",
				income_expense_account_field: row.temporary_opening_account,
				"cost_center": cost_center
			})
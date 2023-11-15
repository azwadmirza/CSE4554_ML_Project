	def update_consumed_qty_for_required_items(self):
		'''update consumed qty from submitted stock entries for that item against
			the work order'''

		for d in self.required_items:
			consumed_qty = frappe.db.sql('''select sum(qty)
				from `tabStock Entry` entry, `tabStock Entry Detail` detail
				where
					entry.work_order = %s
					and (entry.purpose = "Material Consumption for Manufacture"
					or entry.purpose = "Manufacture")
					and entry.docstatus = 1
					and detail.parent = entry.name
					and detail.item_code = %s''', (self.name, d.item_code))[0][0]

			d.db_set('consumed_qty', flt(consumed_qty), update_modified = False)
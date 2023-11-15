	def add_to_stock_entry_detail(self, item_dict, bom_no=None):
		expense_account, cost_center = frappe.db.get_values("Company", self.company, \
			["default_expense_account", "cost_center"])[0]

		for d in item_dict:
			stock_uom = item_dict[d].get("stock_uom") or frappe.db.get_value("Item", d, "stock_uom")

			se_child = self.append('items')
			se_child.s_warehouse = item_dict[d].get("from_warehouse")
			se_child.t_warehouse = item_dict[d].get("to_warehouse")
			se_child.item_code = item_dict[d].get('item_code') or cstr(d)
			se_child.item_name = item_dict[d]["item_name"]
			se_child.description = item_dict[d]["description"]
			se_child.uom = stock_uom
			se_child.stock_uom = stock_uom
			se_child.qty = flt(item_dict[d]["qty"], se_child.precision("qty"))
			se_child.expense_account = item_dict[d].get("expense_account") or expense_account
			se_child.cost_center = item_dict[d].get("cost_center") or cost_center
			se_child.allow_alternative_item = item_dict[d].get("allow_alternative_item", 0)
			se_child.subcontracted_item = item_dict[d].get("main_item_code")
			se_child.original_item = item_dict[d].get("original_item")

			if item_dict[d].get("idx"):
				se_child.idx = item_dict[d].get("idx")

			if se_child.s_warehouse==None:
				se_child.s_warehouse = self.from_warehouse
			if se_child.t_warehouse==None:
				se_child.t_warehouse = self.to_warehouse

			# in stock uom
			se_child.transfer_qty = flt(item_dict[d]["qty"], se_child.precision("qty"))
			se_child.conversion_factor = 1.00

			# to be assigned for finished item
			se_child.bom_no = bom_no
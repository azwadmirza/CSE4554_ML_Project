	def get_transfered_raw_materials(self):
		transferred_materials = frappe.db.sql("""
			select
				item_name, item_code, sum(qty) as qty, sed.t_warehouse as warehouse,
				description, stock_uom, expense_account, cost_center
			from `tabStock Entry` se,`tabStock Entry Detail` sed
			where
				se.name = sed.parent and se.docstatus=1 and se.purpose='Material Transfer for Manufacture'
				and se.work_order= %s and ifnull(sed.t_warehouse, '') != ''
			group by sed.item_code, sed.t_warehouse
		""", self.work_order, as_dict=1)

		materials_already_backflushed = frappe.db.sql("""
			select
				item_code, sed.s_warehouse as warehouse, sum(qty) as qty
			from
				`tabStock Entry` se, `tabStock Entry Detail` sed
			where
				se.name = sed.parent and se.docstatus=1
				and (se.purpose='Manufacture' or se.purpose='Material Consumption for Manufacture')
				and se.work_order= %s and ifnull(sed.s_warehouse, '') != ''
			group by sed.item_code, sed.s_warehouse
		""", self.work_order, as_dict=1)

		backflushed_materials= {}
		for d in materials_already_backflushed:
			backflushed_materials.setdefault(d.item_code,[]).append({d.warehouse: d.qty})

		po_qty = frappe.db.sql("""select qty, produced_qty, material_transferred_for_manufacturing from
			`tabWork Order` where name=%s""", self.work_order, as_dict=1)[0]

		manufacturing_qty = flt(po_qty.qty)
		produced_qty = flt(po_qty.produced_qty)
		trans_qty = flt(po_qty.material_transferred_for_manufacturing)

		for item in transferred_materials:
			qty= item.qty
			req_items = frappe.get_all('Work Order Item',
				filters={'parent': self.work_order, 'item_code': item.item_code},
				fields=["required_qty", "consumed_qty"]
				)
			req_qty = flt(req_items[0].required_qty)
			req_qty_each = flt(req_qty / manufacturing_qty)
			consumed_qty = flt(req_items[0].consumed_qty)

			if trans_qty and manufacturing_qty >= (produced_qty + flt(self.fg_completed_qty)):
				if qty >= req_qty:
					qty = (req_qty/trans_qty) * flt(self.fg_completed_qty)
				else:
					qty = qty - consumed_qty

				if self.purpose == 'Manufacture':
					# If Material Consumption is booked, must pull only remaining components to finish product
					if consumed_qty != 0:
						remaining_qty = consumed_qty - (produced_qty * req_qty_each)
						exhaust_qty = req_qty_each * produced_qty
						if remaining_qty > exhaust_qty :
							if (remaining_qty/(req_qty_each * flt(self.fg_completed_qty))) >= 1:
								qty =0
							else:
								qty = (req_qty_each * flt(self.fg_completed_qty)) - remaining_qty
					else:
						qty = req_qty_each * flt(self.fg_completed_qty)


			elif backflushed_materials.get(item.item_code):
				for d in backflushed_materials.get(item.item_code):
					if d.get(item.warehouse):
						if (qty > req_qty):
							qty = req_qty
							qty-= d.get(item.warehouse)

			if qty > 0:
				self.add_to_stock_entry_detail({
					item.item_code: {
						"from_warehouse": item.warehouse,
						"to_warehouse": "",
						"qty": qty,
						"item_name": item.item_name,
						"description": item.description,
						"stock_uom": item.stock_uom,
						"expense_account": item.expense_account,
						"cost_center": item.buying_cost_center,
					}
				})
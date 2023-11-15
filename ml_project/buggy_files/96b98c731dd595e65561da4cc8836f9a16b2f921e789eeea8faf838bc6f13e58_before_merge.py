	def create_receiver_list(self):
		rec, where_clause = '', ''
		if self.send_to == 'All Customer Contact':
			where_clause = self.customer and " and customer = '%s'" % \
				self.customer.replace("'", "\'") or " and ifnull(customer, '') != ''"
		if self.send_to == 'All Supplier Contact':
			where_clause = self.supplier and " and supplier = '%s'" % \
				self.supplier.replace("'", "\'") or " and ifnull(supplier, '') != ''"
		if self.send_to == 'All Sales Partner Contact':
			where_clause = self.sales_partner and " and sales_partner = '%s'" % \
				self.sales_partner.replace("'", "\'") or " and ifnull(sales_partner, '') != ''"

		if self.send_to in ['All Contact', 'All Customer Contact', 'All Supplier Contact', 'All Sales Partner Contact']:
			rec = frappe.db.sql("""select CONCAT(ifnull(first_name,''), ' ', ifnull(last_name,'')),
				mobile_no from `tabContact` where ifnull(mobile_no,'')!='' and
				docstatus != 2 %s""" % where_clause)

		elif self.send_to == 'All Lead (Open)':
			rec = frappe.db.sql("""select lead_name, mobile_no from `tabLead` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and status='Open'""")

		elif self.send_to == 'All Employee (Active)':
			where_clause = self.department and " and department = '%s'" % \
				self.department.replace("'", "\'") or ""
			where_clause += self.branch and " and branch = '%s'" % \
				self.branch.replace("'", "\'") or ""

			rec = frappe.db.sql("""select employee_name, cell_number from
				`tabEmployee` where status = 'Active' and docstatus < 2 and
				ifnull(cell_number,'')!='' %s""" % where_clause)

		elif self.send_to == 'All Sales Person':
			rec = frappe.db.sql("""select sales_person_name,
				tabEmployee.cell_number from `tabSales Person` left join tabEmployee
				on `tabSales Person`.employee = tabEmployee.name
				where ifnull(tabEmployee.cell_number,'')!=''""")

		rec_list = ''

		for d in rec:
			rec_list += d[0] + ' - ' + d[1] + '\n'
		self.receiver_list = rec_list
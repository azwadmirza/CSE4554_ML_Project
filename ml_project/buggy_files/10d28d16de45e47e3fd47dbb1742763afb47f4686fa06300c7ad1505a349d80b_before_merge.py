def delete_lead_addresses(company_name):
	"""Delete addresses to which leads are linked"""
	leads = frappe.get_all("Lead", filters={"company": company_name})
	leads = [ "'%s'"%row.get("name") for row in leads ]
	addresses = []
	if leads:
		addresses = frappe.db.sql_list("""select parent from `tabDynamic Link` where link_name 
			in ({leads})""".format(leads=",".join(leads)))

		if addresses:
			addresses = ["'%s'"%addr for addr in addresses]

			frappe.db.sql("""delete from tabAddress where name in ({addresses}) and 
				name not in (select distinct dl1.parent from `tabDynamic Link` dl1 
				inner join `tabDynamic Link` dl2 on dl1.parent=dl2.parent 
				and dl1.link_doctype<>dl2.link_doctype)""".format(addresses=",".join(addresses)))

			frappe.db.sql("""delete from `tabDynamic Link` where link_doctype='Lead' 
				and parenttype='Address' and link_name in ({leads})""".format(leads=",".join(leads)))

		frappe.db.sql("""update tabCustomer set lead_name=NULL where lead_name in ({leads})""".format(leads=",".join(leads)))
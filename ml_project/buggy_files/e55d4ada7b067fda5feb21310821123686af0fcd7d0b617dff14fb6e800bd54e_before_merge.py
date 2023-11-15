def execute():
	frappe.reload_doc('subscription', 'doctype', 'subscription')
	frappe.reload_doc('selling', 'doctype', 'sales_order')
	frappe.reload_doc('buying', 'doctype', 'purchase_order')
	frappe.reload_doc('accounts', 'doctype', 'sales_invoice')
	frappe.reload_doc('accounts', 'doctype', 'purchase_invoice')

	for doctype in ['Sales Order', 'Sales Invoice',
		'Purchase Invoice', 'Purchase Invoice']:
		for data in get_data(doctype):
			make_subscription(doctype, data)
def process_deferred_accounting(posting_date=None):
	''' Converts deferred income/expense into income/expense
		Executed via background jobs on every month end '''

	if not posting_date:
		posting_date = today()

	if not cint(frappe.db.get_singles_value('Accounts Settings', 'automatically_process_deferred_accounting_entry')):
		return

	start_date = add_months(today(), -1)
	end_date = add_days(today(), -1)

	for record_type in ('Income', 'Expense'):
		doc = frappe.get_doc(dict(
			doctype='Process Deferred Accounting',
			posting_date=posting_date,
			start_date=start_date,
			end_date=end_date,
			type=record_type
		))

		doc.insert()
		doc.submit()
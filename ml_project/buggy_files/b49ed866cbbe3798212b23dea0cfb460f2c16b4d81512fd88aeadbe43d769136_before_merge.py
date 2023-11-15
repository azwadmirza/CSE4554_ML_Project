def set_gl_entries_by_account(from_date, to_date, root_lft, root_rgt, filters, gl_entries_by_account,
	accounts_by_name, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""

	company_lft, company_rgt = frappe.get_cached_value('Company',
		filters.get('company'),  ["lft", "rgt"])

	additional_conditions = get_additional_conditions(from_date, ignore_closing_entries, filters)
	companies = frappe.db.sql(""" select name, default_currency from `tabCompany`
		where lft >= %(company_lft)s and rgt <= %(company_rgt)s""", {
			"company_lft": company_lft,
			"company_rgt": company_rgt,
		}, as_dict=1)

	currency_info = frappe._dict({
		'report_date': to_date,
		'presentation_currency': filters.get('presentation_currency')
	})

	for d in companies:
		gl_entries = frappe.db.sql("""select gl.posting_date, gl.account, gl.debit, gl.credit, gl.is_opening, gl.company,
			gl.fiscal_year, gl.debit_in_account_currency, gl.credit_in_account_currency, gl.account_currency,
			acc.account_name, acc.account_number
			from `tabGL Entry` gl, `tabAccount` acc where acc.name = gl.account and gl.company = %(company)s
			{additional_conditions} and gl.posting_date <= %(to_date)s and acc.lft >= %(lft)s and acc.rgt <= %(rgt)s
			order by gl.account, gl.posting_date""".format(additional_conditions=additional_conditions),
			{
				"from_date": from_date,
				"to_date": to_date,
				"lft": root_lft,
				"rgt": root_rgt,
				"company": d.name,
				"finance_book": filters.get("finance_book"),
				"company_fb": frappe.db.get_value("Company", d.name, 'default_finance_book')
			},
			as_dict=True)

		if filters and filters.get('presentation_currency') != d.default_currency:
			currency_info['company'] = d.name
			currency_info['company_currency'] = d.default_currency
			convert_to_presentation_currency(gl_entries, currency_info)

		for entry in gl_entries:
			key = entry.account_number or entry.account_name
			validate_entries(key, entry, accounts_by_name)
			gl_entries_by_account.setdefault(key, []).append(entry)

	return gl_entries_by_account
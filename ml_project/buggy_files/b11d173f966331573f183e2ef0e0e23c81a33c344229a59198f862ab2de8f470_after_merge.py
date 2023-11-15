def set_gl_entries_by_account(
		company, from_date, to_date, root_lft, root_rgt, filters, gl_entries_by_account, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""

	additional_conditions = get_additional_conditions(from_date, ignore_closing_entries, filters)

	accounts = frappe.db.sql_list("""select name from `tabAccount`
		where lft >= %s and rgt <= %s and company = %s""", (root_lft, root_rgt, company))

	if accounts:
		additional_conditions += " and account in ({})"\
			.format(", ".join([frappe.db.escape(d) for d in accounts]))

		gl_filters = {
			"company": company,
			"from_date": from_date,
			"to_date": to_date,
			"finance_book": cstr(filters.get("finance_book"))
		}

		if filters.get("include_default_book_entries"):
			gl_filters["company_fb"] = frappe.db.get_value("Company",
				company, 'default_finance_book')

		for key, value in filters.items():
			if value:
				gl_filters.update({
					key: value
				})

		distributed_cost_center_query = ""
		if filters and filters.get('cost_center'):
			distributed_cost_center_query = """
			UNION ALL
			SELECT posting_date,
				account,
				debit*(DCC_allocation.percentage_allocation/100) as debit,
				credit*(DCC_allocation.percentage_allocation/100) as credit,
				is_opening,
				fiscal_year,
				debit_in_account_currency*(DCC_allocation.percentage_allocation/100) as debit_in_account_currency,
				credit_in_account_currency*(DCC_allocation.percentage_allocation/100) as credit_in_account_currency,
				account_currency
			FROM `tabGL Entry`,
			(
				SELECT parent, sum(percentage_allocation) as percentage_allocation
				FROM `tabDistributed Cost Center`
				WHERE cost_center IN %(cost_center)s
				AND parent NOT IN %(cost_center)s
				GROUP BY parent
			) as DCC_allocation
			WHERE company=%(company)s
			{additional_conditions}
			AND posting_date <= %(to_date)s
			AND is_cancelled = 0
			AND cost_center = DCC_allocation.parent
			""".format(additional_conditions=additional_conditions.replace("and cost_center in %(cost_center)s ", ''))

		gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening, fiscal_year, debit_in_account_currency, credit_in_account_currency, account_currency from `tabGL Entry`
			where company=%(company)s
			{additional_conditions}
			and posting_date <= %(to_date)s
			and is_cancelled = 0
			{distributed_cost_center_query}
			order by account, posting_date""".format(
				additional_conditions=additional_conditions,
				distributed_cost_center_query=distributed_cost_center_query), gl_filters, as_dict=True) #nosec

		if filters and filters.get('presentation_currency'):
			convert_to_presentation_currency(gl_entries, get_currency(filters), filters.get('company'))

		for entry in gl_entries:
			gl_entries_by_account.setdefault(entry.account, []).append(entry)

		return gl_entries_by_account
def convert_to_presentation_currency(gl_entries, currency_info):
	"""
	Take a list of GL Entries and change the 'debit' and 'credit' values to currencies
	in `currency_info`.
	:param gl_entries:
	:param currency_info:
	:return:
	"""
	converted_gl_list = []
	presentation_currency = currency_info['presentation_currency']
	company_currency = currency_info['company_currency']

	for entry in gl_entries:
		account = entry['account']
		debit = flt(entry['debit'])
		credit = flt(entry['credit'])
		debit_in_account_currency = flt(entry['debit_in_account_currency'])
		credit_in_account_currency = flt(entry['credit_in_account_currency'])
		account_currency = entry['account_currency']

		if account_currency != presentation_currency:
			value = debit or credit

			date = currency_info['report_date'] if not is_p_or_l_account(account) else entry['posting_date']
			converted_value = convert(value, presentation_currency, company_currency, date)

			if entry.get('debit'):
				entry['debit'] = converted_value

			if entry.get('credit'):
				entry['credit'] = converted_value

		elif account_currency == presentation_currency:
			if entry.get('debit'):
				entry['debit'] = debit_in_account_currency

			if entry.get('credit'):
				entry['credit'] = credit_in_account_currency

		converted_gl_list.append(entry)

	return converted_gl_list
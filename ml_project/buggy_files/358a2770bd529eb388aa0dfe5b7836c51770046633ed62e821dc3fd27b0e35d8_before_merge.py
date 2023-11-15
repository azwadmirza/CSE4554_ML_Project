def get_result(doc, to_date=None):
	doc = frappe.parse_json(doc)
	fields = []
	sql_function_map = {
		'Count': 'count',
		'Sum': 'sum',
		'Average': 'avg',
		'Minimum': 'min',
		'Maximum': 'max'
	}

	function = sql_function_map[doc.function]

	if function == 'count':
		fields = ['{function}(*) as result'.format(function=function)]
	else:
		fields = ['{function}({based_on}) as result'.format(function=function, based_on=doc.aggregate_function_based_on)]

	filters = frappe.parse_json(doc.filters_json)

	if to_date:
		filters.append([doc.document_type, 'creation', '<', to_date, False])

	res = frappe.db.get_all(doc.document_type, fields=fields, filters=filters)
	number = res[0]['result'] if res else 0

	frappe.db.set_value('Number Card', doc.name, 'previous_result', number)
	return number
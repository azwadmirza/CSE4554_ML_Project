def get_details(hub_sync_id=None, doctype='Hub Item'):
	if not hub_sync_id:
		return
	connection = get_client_connection()
	details = connection.get_doc(doctype, hub_sync_id)
	reviews = details.get('reviews')
	if len(reviews):
		for r in reviews:
			r.setdefault('pretty_date', frappe.utils.pretty_date(r.get('modified')))
		details.setdefault('reviews', reviews)
	return details
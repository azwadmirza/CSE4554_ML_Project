def rebuild_for_doctype(doctype):
	"""
	Rebuild entries of doctype's documents in __global_search on change of
	searchable fields
	:param doctype: Doctype
	"""
	if frappe.local.conf.get('disable_global_search'):
		return

	if frappe.local.conf.get('disable_global_search'):
		return

	def _get_filters():
		filters = frappe._dict({ "docstatus": ["!=", 2] })
		if meta.has_field("enabled"):
			filters.enabled = 1
		if meta.has_field("disabled"):
			filters.disabled = 0

		return filters

	meta = frappe.get_meta(doctype)
	if cint(meta.istable) == 1:
		parent_doctypes = frappe.get_all("DocField", fields="parent", filters={
			"fieldtype": ["in", frappe.model.table_fields],
			"options": doctype
		})
		for p in parent_doctypes:
			rebuild_for_doctype(p.parent)

		return

	# Delete records
	delete_global_search_records_for_doctype(doctype)

	parent_search_fields = meta.get_global_search_fields()
	fieldnames = get_selected_fields(meta, parent_search_fields)

	# Get all records from parent doctype table
	all_records = frappe.get_all(doctype, fields=fieldnames, filters=_get_filters())

	# Children data
	all_children, child_search_fields = get_children_data(doctype, meta)
	all_contents = []

	for doc in all_records:
		content = []
		for field in parent_search_fields:
			value = doc.get(field.fieldname)
			if value:
				content.append(get_formatted_value(value, field))

		# get children data
		for child_doctype, records in all_children.get(doc.name, {}).items():
			for field in child_search_fields.get(child_doctype):
				for r in records:
					if r.get(field.fieldname):
						content.append(get_formatted_value(r.get(field.fieldname), field))

		if content:
			# if doctype published in website, push title, route etc.
			published = 0
			title, route = "", ""
			try:
				if hasattr(get_controller(doctype), "is_website_published") and meta.allow_guest_to_view:
					d = frappe.get_doc(doctype, doc.name)
					published = 1 if d.is_website_published() else 0
					title = d.get_title()
					route = d.get("route")
			except ImportError:
				# some doctypes has been deleted via future patch, hence controller does not exists
				pass

			all_contents.append({
				"doctype": frappe.db.escape(doctype),
				"name": frappe.db.escape(doc.name),
				"content": frappe.db.escape(' ||| '.join(content or '')),
				"published": published,
				"title": frappe.db.escape(title or '')[:int(frappe.db.VARCHAR_LEN)],
				"route": frappe.db.escape(route or '')[:int(frappe.db.VARCHAR_LEN)]
			})
	if all_contents:
		insert_values_for_multiple_docs(all_contents)
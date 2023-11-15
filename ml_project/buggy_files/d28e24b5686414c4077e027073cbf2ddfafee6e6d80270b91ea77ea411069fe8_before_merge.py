def get_transitions(doc, workflow = None):
	'''Return list of possible transitions for the given doc'''
	doc = frappe.get_doc(frappe.parse_json(doc))

	if doc.is_new():
		return []

	frappe.has_permission(doc, 'read', throw=True)
	roles = frappe.get_roles()

	if not workflow:
		workflow = get_workflow(doc.doctype)
	current_state = doc.get(workflow.workflow_state_field)

	if not current_state:
		frappe.throw(_('Workflow State not set'), WorkflowStateError)

	transitions = []
	for transition in workflow.transitions:
		if transition.state == current_state and transition.allowed in roles:
			if transition.condition:
				# if condition, evaluate
				# access to frappe.db.get_value and frappe.db.get_list
				success = frappe.safe_eval(transition.condition,
					dict(frappe = frappe._dict(
						db = frappe._dict(get_value = frappe.db.get_value, get_list=frappe.db.get_list),
						session = frappe.session
					)),
					dict(doc = doc))
				if not success:
					continue
			transitions.append(transition.as_dict())

	return transitions
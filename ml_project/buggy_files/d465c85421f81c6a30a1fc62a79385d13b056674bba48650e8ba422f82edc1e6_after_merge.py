def make_student_group():
	for term in frappe.db.get_list("Academic Term"):
		for program in frappe.db.get_list("Program"):
			sg_tool = frappe.new_doc("Student Group Creation Tool")
			sg_tool.academic_year = "2017-18"
			sg_tool.academic_term = term.name
			sg_tool.program = program.name
			for d in sg_tool.get_courses():
				d = frappe._dict(d)
				student_group = frappe.new_doc("Student Group")
				student_group.student_group_name = d.student_group_name
				student_group.group_based_on = d.group_based_on
				student_group.program = program.name
				student_group.course = d.course
				student_group.batch = d.batch
				student_group.academic_term = term.name
				student_group.academic_year = "2017-18"
				student_group.save()
			frappe.db.commit()
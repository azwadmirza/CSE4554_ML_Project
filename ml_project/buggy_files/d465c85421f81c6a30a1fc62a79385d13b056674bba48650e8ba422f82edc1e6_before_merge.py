def make_student_group():
	for d in frappe.db.get_list("Academic Term"):
		sg_tool = frappe.new_doc("Student Group Creation Tool")
		sg_tool.academic_year = "2016-17"
		sg_tool.academic_term = d.name
		sg_tool.courses = sg_tool.get_courses()
		sg_tool.create_student_groups()
		frappe.db.commit()
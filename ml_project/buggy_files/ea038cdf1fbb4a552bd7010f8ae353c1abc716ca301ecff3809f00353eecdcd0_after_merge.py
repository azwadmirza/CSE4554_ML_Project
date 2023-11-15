def assign_student_group(student, student_name, program, courses, batch):
	course_list = [d["course"] for d in courses]
	for d in frappe.get_list("Student Group", fields=("name"), filters={"program": program, "course":("in", course_list)}):
		student_group = frappe.get_doc("Student Group", d.name)
		student_group.append("students", {"student": student, "student_name": student_name,
			"group_roll_number":len(student_group.students)+1, "active":1})
		student_group.save()
	student_batch = frappe.get_list("Student Group", fields=("name"), filters={"program": program, "group_based_on":"Batch", "batch":batch})[0]
	student_batch_doc = frappe.get_doc("Student Group", student_batch.name)
	student_batch_doc.append("students", {"student": student, "student_name": student_name,
		"group_roll_number":len(student_batch_doc.students)+1, "active":1})
	student_batch_doc.save()
	frappe.db.commit()
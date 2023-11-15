def assign_student_group(student, program):
	courses = []
	for d in frappe.get_list("Program Course", fields=("course"), filters={"parent": program }):
		courses.append(d.course)

	for d in xrange(3):
		course = random.choice(courses)
		random_sg = get_random("Student Group", {"course": course})
		if random_sg:
			student_group = frappe.get_doc("Student Group", random_sg)
			student_group.append("students", {"student": student})
			student_group.save()
		courses.remove(course)
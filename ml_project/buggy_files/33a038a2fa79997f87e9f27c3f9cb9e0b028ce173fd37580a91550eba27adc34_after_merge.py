def enroll_random_student(current_date):
	batch = ["Section-A", "Section-B"]
	random_student = get_random("Student Applicant", {"application_status": "Approved"})
	if random_student:
		enrollment = enroll_student(random_student)
		enrollment.academic_year = get_random("Academic Year")
		enrollment.enrollment_date = current_date
		enrollment.student_batch_name = batch[weighted_choice([9,3])]
		fee_schedule = get_fee_schedule(enrollment.program)
		for fee in fee_schedule:
			enrollment.append("fees", fee)
		enrolled_courses = get_course(enrollment.program)
		for course in enrolled_courses:
			enrollment.append("courses", course)
		enrollment.submit()
		frappe.db.commit()
		assign_student_group(enrollment.student, enrollment.student_name, enrollment.program,
			enrolled_courses, enrollment.student_batch_name)
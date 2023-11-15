def enroll_random_student(current_date):
	random_student = get_random("Student Applicant", {"application_status": "Approved"})
	if random_student:
		enrollment = enroll_student(random_student)
		enrollment.academic_year = get_random("Academic Year")
		enrollment.enrollment_date = current_date
		fee_schedule = get_fee_schedule(enrollment.program)
		for fee in fee_schedule:
			enrollment.append("fees", fee)
		enrollment.submit()
		frappe.db.commit()
		assign_student_group(enrollment.student, enrollment.program)
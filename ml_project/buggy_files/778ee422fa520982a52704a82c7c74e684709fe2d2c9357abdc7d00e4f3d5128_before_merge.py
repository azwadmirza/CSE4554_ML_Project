def work():
	frappe.set_user(frappe.db.get_global('demo_schools_user'))
	for d in xrange(20):
		approve_random_student_applicant()
		enroll_random_student(frappe.flags.current_date)
	if frappe.flags.current_date.weekday()== 0:
		make_course_schedule(frappe.flags.current_date, frappe.utils.add_days(frappe.flags.current_date, 5))	
	mark_student_attendance(frappe.flags.current_date)
	make_fees()
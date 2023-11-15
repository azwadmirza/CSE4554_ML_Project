def mark_student_attendance(current_date):
	status = ["Present", "Absent"]
	for d in frappe.db.get_list("Course Schedule", filters={"schedule_date": current_date}, fields=("name", "student_group")):
		students = get_student_group_students(d.student_group)
		for stud in students:
			make_attendance_records(stud.student, stud.student_name, d.name, status[weighted_choice([9,4])])
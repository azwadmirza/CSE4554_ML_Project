def mark_student_attendance(current_date):
	status = ["Present", "Absent"]
	for d in frappe.db.get_list("Student Group", filters={"group_based_on": "Batch"}):
		students = get_student_group_students(d.name)
		for stud in students:
			make_attendance_records(stud.student, stud.student_name, status[weighted_choice([9,4])], None, d.name, current_date)
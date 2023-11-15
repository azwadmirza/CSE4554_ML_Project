def setup_data():
	frappe.flags.mute_emails = True
	make_masters()
	setup_item()
	make_student_applicants()
	make_student_group()
	make_fees_category()
	make_fees_structure()
	make_assessment_groups()
	frappe.db.commit()
	frappe.clear_cache()
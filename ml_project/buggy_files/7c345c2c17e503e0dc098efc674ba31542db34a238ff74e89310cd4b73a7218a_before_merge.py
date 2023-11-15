def make_masters():
	import_json("Room")
	import_json("Department")
	import_json("Instructor")
	import_json("Course")
	import_json("Program")
	frappe.db.commit()
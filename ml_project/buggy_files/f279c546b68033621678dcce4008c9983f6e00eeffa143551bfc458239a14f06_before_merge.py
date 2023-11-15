def make_fees_structure():
	for d in frappe.db.get_list("Program"):
		program = frappe.get_doc("Program", d.name)
		for academic_term in ["Semester 1", "Semester 2", "Semester 3"]:
			fee_structure = frappe.new_doc("Fee Structure")
			fee_structure.program = d.name
			fee_structure.academic_term = random.choice(frappe.db.get_list("Academic Term")).name
			for j in range(1,4):
				temp = {"fees_category": random.choice(frappe.db.get_list("Fee Category")).name , "amount" : random.randint(500,1000)}
				fee_structure.append("components", temp)
			fee_structure.insert()
			program.append("fees", {"academic_term": academic_term, "fee_structure": fee_structure.name, "amount": fee_structure.total_amount})
		program.save()
	frappe.db.commit()
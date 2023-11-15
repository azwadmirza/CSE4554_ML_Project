def check_valid_domain(domain_text):
    domain_text = domain_text.split('@',1)[-1].lower()
    sql = "SELECT * FROM registration WHERE :domain LIKE domain;"
    result = ub.session.query(ub.Registration).from_statement(text(sql)).params(domain=domain_text).all()
    return len(result)
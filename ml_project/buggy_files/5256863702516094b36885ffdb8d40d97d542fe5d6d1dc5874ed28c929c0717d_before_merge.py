def check_valid_domain(domain_text):
    # result = session.query(Notification).from_statement(text(sql)).params(id=5).all()
    #ToDo: check possible SQL injection
    domain_text = domain_text.split('@',1)[-1].lower()
    sql = "SELECT * FROM registration WHERE '%s' LIKE domain;" % domain_text
    result = ub.session.query(ub.Registration).from_statement(text(sql)).all()
    return len(result)
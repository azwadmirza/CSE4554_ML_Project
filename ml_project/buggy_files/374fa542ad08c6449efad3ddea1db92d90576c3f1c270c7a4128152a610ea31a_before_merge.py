def check_auth(username, password):
    user = ub.session.query(ub.User).filter(func.lower(ub.User.nickname) == username.lower()).first()
    return bool(user and check_password_hash(user.password, password))
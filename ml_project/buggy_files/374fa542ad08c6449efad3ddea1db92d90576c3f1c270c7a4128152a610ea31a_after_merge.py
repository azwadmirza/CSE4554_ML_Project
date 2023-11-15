def check_auth(username, password):
    if sys.version_info.major == 3:
        username=username.encode('windows-1252')
    user = ub.session.query(ub.User).filter(func.lower(ub.User.nickname) == username.decode('utf-8').lower()).first()
    return bool(user and check_password_hash(user.password, password))
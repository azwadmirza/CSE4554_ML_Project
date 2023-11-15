def login_check():
    users = db.mgmt_users
    # validate username and password
    username = request.form.get('username')
    password =request.form.get('password')
    person = User.get(username)
    try:
        if person and pbkdf2_sha256.verify(password, person.password):
            login_user(person)
            return render_template('admin.html',status=["logged_in", "success"])
        else:
            return render_template('login.html', status=["wrong_combination", "warning"])
    except:
        return render_template('login.html', status=["outdated_database", "error"])
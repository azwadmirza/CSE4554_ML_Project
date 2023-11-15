def login_check():
    # validate username and password
    username = request.form.get('username')
    password = hashlib.sha256(bytes(request.form.get('password'), "utf-8")).hexdigest()

    person = User.get(username)
    if person and person.password == password:
        login_user(person)
        return render_template('admin.html',status=["logged_in", "success"])
    else:
        return render_template('login.html', status=["wrong_combination", "error"])
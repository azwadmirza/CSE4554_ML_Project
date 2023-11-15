def login_check():
    users = db.mgmt_users
    # validate username and password
    username = request.form.get('username')
    # get salt
    if users.find({'username':username}).count()>0:
        if users.find({'username':username,'salt':{'$exists':True}}).count()>0:
            salt = (list(users.find({'username':username}))[0])['salt']
        else:
            return render_template('login.html',status=["outdated_database", "error"])
        # catch empyt
    else:
        salt = bytearray()
    password = hashlib.sha256(salt + bytes(request.form.get('password'), "utf-8")).hexdigest()
    person = User.get(username)
    if person and person.password == password:
        login_user(person)
        return render_template('admin.html',status=["logged_in", "success"])
    else:
        return render_template('login.html', status=["wrong_combination", "warning"])
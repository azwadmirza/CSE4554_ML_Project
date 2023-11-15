def login():
    if request.method == 'POST':
        codename = request.form['codename']
        if valid_codename(codename):
            flagged = check_flagged(codename)
            session.update(codename=codename, flagged=flagged, logged_in=True)
            return redirect(url_for('lookup'))
        else:
            flash("Sorry, that is not a recognized codename.", "error")
    return render_template('login.html')
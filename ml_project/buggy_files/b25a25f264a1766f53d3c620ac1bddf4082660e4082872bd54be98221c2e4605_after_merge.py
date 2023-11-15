def logout():
	# logout from user manager...
	_logout(current_user)

	# ... and from flask login (and principal)
	logout_user()

	# ... and send an active logout session cookie
	r = make_response(NO_CONTENT)
	r.set_cookie("active_logout", "true")

	return r
def logout():
	# logout from user manager...
	_logout(current_user)

	# ... and from flask login (and principal)
	logout_user()

	return NO_CONTENT
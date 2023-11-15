def deleteHost(ip):
	delForm = forms.DeleteForm()

	if delForm.validate_on_submit():
		deleted = current_app.elastic.delete_host(ip)
		if deleted > 0:
			flash("Successfully deleted host %s" % ip, "success")
			return redirect(url_for('main.search'))
		else:
			flash("Couldn't delete host: %s" % ip, "danger")
	else:
		flash("Couldn't validate form!")
		return redirect(request.referrer)
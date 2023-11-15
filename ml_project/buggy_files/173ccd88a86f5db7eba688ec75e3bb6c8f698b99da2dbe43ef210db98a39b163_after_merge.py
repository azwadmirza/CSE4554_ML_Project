def deleteHost(ip):
	delForm = forms.DeleteForm()

	if delForm.validate_on_submit():
		deleted = current_app.elastic.delete_host(ip)
		if deleted > 0:
			flash(f"Successfully deleted {deleted - 1 if deleted > 1 else deleted} scans for {ip}", "success")
			return redirect(url_for('main.browse'))
		else:
			flash(f"Couldn't delete host: {ip}", "danger")
	else:
		flash("Couldn't validate form!")
		return redirect(request.referrer)
def deleteScan(scan_id):
	delForm = forms.DeleteForm()

	if delForm.validate_on_submit():
		deleted = current_app.elastic.delete_scan(scan_id)
		if deleted in [1, 2]:
			flash("Successfully deleted scan %s." % scan_id, "success")
			if request.referrer:
				if scan_id in request.referrer:
					redirectLoc = request.referrer.rsplit(scan_id)[0]
				else:
					redirectLoc = request.referrer
			else:
				redirectLoc = url_for('main.browse')
			return redirect(redirectLoc)
		else:
			flash("Could not delete scan %s." % scan_id, "danger")
			return redirect(request.referrer or url_for('main.browse'))
	else:
		flash("Couldn't validate form!")
		return redirect(request.referrer)
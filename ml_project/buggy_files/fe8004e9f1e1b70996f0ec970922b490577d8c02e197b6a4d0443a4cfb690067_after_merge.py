def admin():
	configForm = forms.ConfigForm()
	configItems = current_app.config
	if configForm.validate_on_submit():
		for fieldname, fieldvalue in configForm.data.items():
			if fieldname.upper() in ["SUBMIT", "CSRF_TOKEN"]:
				continue
			current_app.config[fieldname.upper()] = fieldvalue
			confitem = ConfigItem.query.filter_by(name=fieldname.upper()).first()
			confitem.value = str(fieldvalue)
			db.session.add(confitem)
		db.session.commit()
	return render_template("admin/index.html", configForm=configForm, configItems=configItems)
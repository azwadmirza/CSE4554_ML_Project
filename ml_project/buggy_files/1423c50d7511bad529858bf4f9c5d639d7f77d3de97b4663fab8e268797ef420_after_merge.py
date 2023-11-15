def random_host():
	random_host = current_app.elastic.random_host()
	# This would most likely occur when there are no hosts up in the index, so just throw a 404
	if not random_host:
		abort(404)
	ip = random_host['ip']
	info, context = hostinfo(ip)
	delForm = DeleteForm()
	delHostForm = DeleteForm()
	rescanForm = RescanForm()

	version = determine_data_version(context)
	template_str = f"host/versions/{version}/summary.html"
	return render_template(
		template_str,
		**context,
		host=context,
		info=info,
		delForm=delForm,
		delHostForm=delHostForm,
		rescanForm=rescanForm
	)
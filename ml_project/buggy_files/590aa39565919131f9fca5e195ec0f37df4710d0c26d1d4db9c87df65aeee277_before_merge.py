def host_historical_result(ip, scan_id):
	delForm = DeleteForm()
	delHostForm = DeleteForm()
	rescanForm = RescanForm()
	info, context = hostinfo(ip)
	count, context = current_app.elastic.gethost_scan_id(scan_id)

	version = determine_data_version(context)
	template_str = f"host/versions/{version}/summary.html"
	return render_template(
		template_str,
		host=context,
		info=info,
		**context,
		delForm=delForm,
		delHostForm=delHostForm,
		rescanForm=rescanForm
	)
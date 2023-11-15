def host_history(ip):
	info, context = hostinfo(ip)
	page = int(request.args.get('p', 1))
	searchOffset = current_user.results_per_page * (page - 1)

	delHostForm = DeleteForm()
	rescanForm = RescanForm()

	count, context = current_app.elastic.gethost_history(
		ip, current_user.results_per_page, searchOffset)
	if count == 0:
		abort(404)
	next_url = url_for('host.host_history', ip=ip, p=page + 1) \
		if count > page * current_user.results_per_page else None
	prev_url = url_for('host.host_history', ip=ip, p=page - 1) \
		if page > 1 else None

	# TODO Hardcoding the version here is bad. Revisit this.
	return render_template(
		"host/versions/0.6.5/history.html",
		ip=ip, info=info,
		page=page,
		numresults=count,
		hosts=context,
		next_url=next_url,
		prev_url=prev_url,
		delHostForm=delHostForm,
		rescanForm=rescanForm
	)
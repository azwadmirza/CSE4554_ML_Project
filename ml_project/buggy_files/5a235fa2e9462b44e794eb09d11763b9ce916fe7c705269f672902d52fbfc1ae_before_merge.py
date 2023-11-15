def search():
	query = request.args.get('query', '')
	page = int(request.args.get('page', 1))
	format = request.args.get('format', '')
	scan_ids = request.args.get('includeScanIDs', '')
	includeHistory = request.args.get('includeHistory', False)

	results_per_page = current_user.results_per_page
	if includeHistory:
		searchIndex = "nmap_history"
	else:
		searchIndex = "nmap"

	searchOffset = results_per_page * (page - 1)
	count, context = current_app.elastic.search(query, results_per_page, searchOffset, searchIndex=searchIndex)
	totalHosts = current_app.elastic.totalHosts()

	if includeHistory:
		next_url = url_for('main.search', query=query, page=page + 1, includeHistory=includeHistory) \
			if count > page * results_per_page else None
		prev_url = url_for('main.search', query=query, page=page - 1, includeHistory=includeHistory) \
			if page > 1 else None
	else:
		next_url = url_for('main.search', query=query, page=page + 1) \
			if count > page * results_per_page else None
		prev_url = url_for('main.search', query=query, page=page - 1) \
			if page > 1 else None

	# what kind of output are we looking for?
	if format == 'hostlist':
		hostlist = []
		for host in context:
			if scan_ids:
				hostlist.append(str(host['ip']) + ',' + str(host['scan_id']))
			else:
				hostlist.append(str(host['ip']))
		return Response('\n'.join(hostlist), mimetype='text/plain')
	else:
		return render_template("search.html", query=query, numresults=count, totalHosts=totalHosts, page=page, hosts=context, next_url=next_url, prev_url=prev_url)
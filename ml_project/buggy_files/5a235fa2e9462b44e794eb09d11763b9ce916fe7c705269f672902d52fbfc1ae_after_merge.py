def search():
	''' Return search results for a given query '''
	query = request.args.get('query', '')
	page = int(request.args.get('page', 1))
	format = request.args.get('format', '')
	scan_ids = request.args.get('includeScanIDs', '')
	includeHistory = request.args.get('includeHistory', False)

	results_per_page, search_offset = results_offset(page)

	searchIndex = "nmap_history" if includeHistory else "nmap"

	count, context = current_app.elastic.search(results_per_page, search_offset, query=query, searchIndex=searchIndex)
	totalHosts = current_app.elastic.total_hosts()

	if includeHistory:
		next_url, prev_url = build_pagination_urls('main.search', page, count, query=query, includeHistory=includeHistory)
	else:
		next_url, prev_url = build_pagination_urls('main.search', page, count, query=query)

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
		return render_template(
			"main/search.html",
			query=query,
			numresults=count,
			totalHosts=totalHosts,
			page=page,
			hosts=context,
			next_url=next_url,
			prev_url=prev_url
		)
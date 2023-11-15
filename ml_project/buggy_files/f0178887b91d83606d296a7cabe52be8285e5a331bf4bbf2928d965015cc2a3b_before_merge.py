def export_scan(ip, scan_id, ext):
	if ext not in ['xml', 'nmap', 'gnmap', 'json']:
		abort(404)

	export_field = f"{ext}_data"

	if ext == 'json':
		mime = "application/json"
	else:
		mime = "text/plain"

	count, context = current_app.elastic.gethost_scan_id(scan_id)
	if ext == 'json' and count > 0:
		return Response(json.dumps(context), mimetype=mime)
	elif count > 0 and export_field in context:
		return Response(context[export_field], mimetype=mime)
	else:
		abort(404)
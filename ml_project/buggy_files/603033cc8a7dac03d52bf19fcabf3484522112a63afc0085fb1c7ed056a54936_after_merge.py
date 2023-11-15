def application(request):
	response = None

	try:
		rollback = True

		init_request(request)

		frappe.recorder.record()
		frappe.monitor.start()
		frappe.rate_limiter.apply()

		if frappe.local.form_dict.cmd:
			response = frappe.handler.handle()

		elif frappe.request.path.startswith("/api/"):
			response = frappe.api.handle()

		elif frappe.request.path.startswith('/backups'):
			response = frappe.utils.response.download_backup(request.path)

		elif frappe.request.path.startswith('/private/files/'):
			response = frappe.utils.response.download_private_file(request.path)

		elif frappe.local.request.method in ('GET', 'HEAD', 'POST'):
			response = frappe.website.render.render()

		else:
			raise NotFound

	except HTTPException as e:
		return e

	except frappe.SessionStopped as e:
		response = frappe.utils.response.handle_session_stopped()

	except Exception as e:
		response = handle_exception(e)

	else:
		rollback = after_request(rollback)

	finally:
		if frappe.local.request.method in ("POST", "PUT") and frappe.db and rollback:
			frappe.db.rollback()

		# set cookies
		if response and hasattr(frappe.local, 'cookie_manager'):
			frappe.local.cookie_manager.flush_cookies(response=response)

		frappe.rate_limiter.update()
		frappe.monitor.stop(response)
		frappe.recorder.dump()

		frappe.logger("frappe.web", allow_site=frappe.local.site).info({
			"site": get_site_name(request.host),
			"remote_addr": getattr(request, "remote_addr", "NOTFOUND"),
			"base_url": getattr(request, "base_url", "NOTFOUND"),
			"full_path": getattr(request, "full_path", "NOTFOUND"),
			"method": getattr(request, "method", "NOTFOUND"),
			"scheme": getattr(request, "scheme", "NOTFOUND"),
			"http_status_code": getattr(response, "status_code", "NOTFOUND")
		})

		if response and hasattr(frappe.local, 'rate_limiter'):
			response.headers.extend(frappe.local.rate_limiter.headers())

		frappe.destroy()

	return response
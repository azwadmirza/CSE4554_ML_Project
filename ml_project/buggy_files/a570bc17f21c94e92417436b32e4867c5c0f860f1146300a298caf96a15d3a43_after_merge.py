def make_site_config(db_name=None, db_password=None, site_config=None, db_type=None, db_host=None, db_port=None):
	frappe.create_folder(os.path.join(frappe.local.site_path))
	site_file = get_site_config_path()

	if not os.path.exists(site_file):
		if not (site_config and isinstance(site_config, dict)):
			site_config = get_conf_params(db_name, db_password)

			if db_type:
				site_config['db_type'] = db_type

			if db_host:
				site_config['db_host'] = db_host

			if db_port:
				site_config['db_port'] = db_port

		with open(site_file, "w") as f:
			f.write(json.dumps(site_config, indent=1, sort_keys=True))
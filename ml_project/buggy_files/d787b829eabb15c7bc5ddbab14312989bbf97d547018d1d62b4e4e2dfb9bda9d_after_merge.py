def install_db(root_login="root", root_password=None, db_name=None, source_sql=None,
			   admin_password=None, verbose=True, force=0, site_config=None, reinstall=False,
			   db_type=None, db_host=None, db_port=None,
			   db_password=None, no_mariadb_socket=False):
	from frappe.database import setup_database

	if not db_type:
		db_type = frappe.conf.db_type or 'mariadb'

	make_conf(db_name, site_config=site_config, db_password=db_password, db_type=db_type, db_host=db_host, db_port=db_port)
	frappe.flags.in_install_db = True

	frappe.flags.root_login = root_login
	frappe.flags.root_password = root_password
	setup_database(force, source_sql, verbose, no_mariadb_socket)

	frappe.conf.admin_password = frappe.conf.admin_password or admin_password

	remove_missing_apps()

	frappe.db.create_auth_table()
	frappe.db.create_global_search_table()
	frappe.db.create_user_settings_table()

	frappe.flags.in_install_db = False
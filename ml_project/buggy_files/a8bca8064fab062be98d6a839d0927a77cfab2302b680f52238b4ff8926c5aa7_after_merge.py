def make_conf(db_name=None, db_password=None, site_config=None, db_type=None, db_host=None, db_port=None):
	site = frappe.local.site
	make_site_config(db_name, db_password, site_config, db_type=db_type, db_host=db_host, db_port=db_port)
	sites_path = frappe.local.sites_path
	frappe.destroy()
	frappe.init(site, sites_path=sites_path)
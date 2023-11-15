    def start(self):
        hub = JupyterHub(parent=self)
        hub.load_config_file(hub.config_file)
        self.log = hub.log
        if (hub.db_url.startswith('sqlite:///')):
            db_file = hub.db_url.split(':///', 1)[1]
            self._backup_db_file(db_file)
        self.log.info("Upgrading %s", hub.db_url)
        dbutil.upgrade(hub.db_url)
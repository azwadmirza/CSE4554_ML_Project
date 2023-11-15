    def add_db(self, db_conf):
        """Add database config to this watcher."""
        self._check_conf_types(db_conf, self.db_defaults_types)
        db_conf = deepcopy(db_conf)
        db_type = db_conf.pop('type')
        db_conf['db_type'] = db_type
        self.update(db_conf)
        test_config_condition(
            self.file is not None and not
            (os.path.dirname(self.file) and os.access(os.path.dirname(self.file), os.W_OK)),
            '%s is not writable' % self.file)
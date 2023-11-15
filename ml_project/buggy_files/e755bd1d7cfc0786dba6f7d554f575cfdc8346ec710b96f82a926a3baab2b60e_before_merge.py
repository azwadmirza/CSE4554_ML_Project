    def add_db(self, db_conf):
        """Add database config to this watcher."""
        db_conf = deepcopy(db_conf)
        db_type = db_conf.pop('type')
        db_conf['db_type'] = db_type
        self.update(db_conf)
    def augment(self, resources):
        session = local_session(self.session_factory)
        if self.account_id is None:
            self.account_id = get_account_id(session)
        _rds_tags(
            self.query.resolve(self.resource_type),
            resources, self.session_factory, self.executor_factory,
            self.account_id, region=self.config.region)
        return resources
    def augment(self, resources):
        _rds_tags(
            self.get_model(),
            resources, self.session_factory, self.executor_factory,
            self.arn_generator)
        return resources
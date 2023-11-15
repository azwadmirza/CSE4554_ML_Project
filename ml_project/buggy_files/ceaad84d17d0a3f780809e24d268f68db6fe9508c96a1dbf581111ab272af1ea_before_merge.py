    def process_resource_set(self, resources, tags):
        client = local_session(self.manager.session_factory).client('rds')
        for r in resources:
            arn = "arn:aws:rds:%s:%s:db:%s" % (
                self.manager.config.region, self.manager.account_id,
                r['DBInstanceIdentifier'])
            client.add_tags_to_resource(ResourceName=arn, Tags=tags)
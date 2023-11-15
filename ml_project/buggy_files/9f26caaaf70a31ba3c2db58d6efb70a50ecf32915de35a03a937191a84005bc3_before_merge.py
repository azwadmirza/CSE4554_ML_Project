    def process_resource_set(self, resources, tag_keys):
        client = local_session(
            self.manager.session_factory).client('rds')
        for r in resources:
            arn = "arn:aws:rds:%s:%s:db:%s" % (
                self.manager.config.region, self.manager.account_id,
                r['DBInstanceIdentifier'])
            client.remove_tags_from_resource(
                ResourceName=arn, TagKeys=tag_keys)
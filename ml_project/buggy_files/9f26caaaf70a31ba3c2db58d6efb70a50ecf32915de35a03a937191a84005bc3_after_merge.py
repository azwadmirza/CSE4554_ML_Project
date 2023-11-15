    def process_resource_set(self, resources, tag_keys):
        client = local_session(
            self.manager.session_factory).client('rds')
        for r in resources:
            arn = self.manager.arn_generator.generate(r['DBInstanceIdentifier'])
            client.remove_tags_from_resource(
                ResourceName=arn, TagKeys=tag_keys)
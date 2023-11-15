    def process_resource_set(self, resources, tags):
        client = local_session(self.manager.session_factory).client('rds')
        for r in resources:
            arn = self.manager.arn_generator.generate(r['DBInstanceIdentifier'])
            client.add_tags_to_resource(ResourceName=arn, Tags=tags)
    def get_resources(self, resource_ids):
        client = local_session(self.manager.session_factory).client('es')
        return client.describe_elasticsearch_domains(
            DomainNames=resource_ids)['DomainStatusList']
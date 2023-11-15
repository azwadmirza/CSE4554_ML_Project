    def set_password(self, service, repo_url, password):
        asyncio.set_event_loop(asyncio.new_event_loop())
        collection = secretstorage.get_default_collection(self.connection)
        attributes = {
            'application': 'Vorta',
            'service': service,
            'repo_url': repo_url,
            'xdg:schema': 'org.freedesktop.Secret.Generic'}
        collection.create_item(repo_url, attributes, password, replace=True)
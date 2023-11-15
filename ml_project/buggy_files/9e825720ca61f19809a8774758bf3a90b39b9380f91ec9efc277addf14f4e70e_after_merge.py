    def get_password(self, service, repo_url):
        if self.is_unlocked:
            asyncio.set_event_loop(asyncio.new_event_loop())
            collection = secretstorage.get_default_collection(self.connection)
            attributes = {'application': 'Vorta', 'service': service, 'repo_url': repo_url}
            items = list(collection.search_items(attributes))
            logger.debug('Found %i passwords matching repo URL.', len(items))
            if len(items) > 0:
                return items[0].get_secret().decode("utf-8")
        return None
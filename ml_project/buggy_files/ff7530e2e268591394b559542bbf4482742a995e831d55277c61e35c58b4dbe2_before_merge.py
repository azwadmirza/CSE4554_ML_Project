    def __init__(self, client_cache, current_version, out, manager):
        self.client_cache = client_cache
        self.manager = manager
        super(ClientMigrator, self).__init__(client_cache.conan_folder, client_cache.store,
                                             current_version, out)
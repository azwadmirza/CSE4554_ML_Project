    def __init__(self, client_cache, current_version, out):
        self.client_cache = client_cache
        super(ClientMigrator, self).__init__(client_cache.conan_folder, client_cache.store,
                                             current_version, out)
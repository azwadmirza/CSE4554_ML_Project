    def __init__(self, opts, valid_providers=VALID_PROVIDERS, cache_root=None):
        self.opts = opts
        self.valid_providers = valid_providers
        self.get_provider()
        if cache_root is not None:
            self.cache_root = cache_root
        else:
            self.cache_root = os.path.join(self.opts['cachedir'], self.role)
        self.env_cache = os.path.join(self.cache_root, 'envs.p')
        self.hash_cachedir = os.path.join(
            self.cache_root, self.role, 'hash')
        self.file_list_cachedir = os.path.join(
            self.opts['cachedir'], 'file_lists', self.role)
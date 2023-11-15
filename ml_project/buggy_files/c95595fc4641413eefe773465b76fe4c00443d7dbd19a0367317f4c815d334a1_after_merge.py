    def __init__(self, meta_store=None):
        self.meta_store = meta_store or RemoteMetaStore.remote()
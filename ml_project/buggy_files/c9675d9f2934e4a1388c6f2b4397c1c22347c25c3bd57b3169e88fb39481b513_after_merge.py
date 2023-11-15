    def __iter__(self):
        return iter(ray.get(self.meta_store.chunk_keys.remote()))
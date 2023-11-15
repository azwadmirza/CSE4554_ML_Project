    def __delitem__(self, key):
        ray.wait([self.meta_store.delete_keys.remote(key)])
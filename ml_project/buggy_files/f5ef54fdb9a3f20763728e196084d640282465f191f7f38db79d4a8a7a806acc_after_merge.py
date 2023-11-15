    def __getitem__(self, item):
        meta: ChunkMeta = ray.get(self.meta_store.get_meta.remote(item))
        return ray.get(meta.object_id)
    def __setitem__(self, key, value):
        object_id = ray.put(value)
        shape = getattr(value, 'shape', None)
        meta = ChunkMeta(shape=shape, object_id=object_id)
        set_meta = self.meta_store.set_meta.remote(key, meta)
        ray.wait([object_id, set_meta])
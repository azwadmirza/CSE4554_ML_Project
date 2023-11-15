    def update(self, mapping: Dict):
        tasks = []
        for k, v in mapping.items():
            object_id = ray.put(v)
            tasks.append(object_id)
            shape = getattr(v, 'shape', None)
            meta = ChunkMeta(shape=shape, object_id=object_id)
            set_meta = self.meta_store.set_meta.remote(k, meta)
            tasks.append(set_meta)
        ray.wait(tasks)
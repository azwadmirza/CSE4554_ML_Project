    def __getitem__(self, item):
        return ray.get(self.ray_dict_ref.getitem.remote(item))
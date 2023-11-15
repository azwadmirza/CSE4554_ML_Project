    def __delitem__(self, key):
        ray.get(self.ray_dict_ref.delitem.remote(key))
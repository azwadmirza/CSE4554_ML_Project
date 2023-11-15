    def __setitem__(self, key, value):
        ray.get(self.ray_dict_ref.setitem.remote(key, value))
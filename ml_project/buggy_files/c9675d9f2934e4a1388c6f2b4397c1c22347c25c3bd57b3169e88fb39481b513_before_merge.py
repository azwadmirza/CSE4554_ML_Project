    def __iter__(self):
        return iter(ray.get(self.ray_dict_ref.keys.remote()))
    def get_shape(self, ds_id, ds_info):
        var_path = ds_info.get('file_key', 'observation_data/{}'.format(ds_id.name))
        return self.get(var_path + '/shape', 1)
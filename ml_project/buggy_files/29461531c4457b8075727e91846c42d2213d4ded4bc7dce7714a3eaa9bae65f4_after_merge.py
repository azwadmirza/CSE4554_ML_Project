    def get_metadata(self, dataset_id, ds_info):
        var_name = ds_info.get('file_key', dataset_id.name)
        shape = self.get_shape(dataset_id, ds_info)
        info = getattr(self[var_name], 'attrs', {})
        info['shape'] = shape
        info.update(ds_info)
        u = info.get('units')
        if u in CF_UNITS:
            # CF compliance
            info['units'] = CF_UNITS[u]

        info['sensor'] = self.get_sensor(self['/attr/Sensor_Name'])
        info['platform'] = self.get_platform(self['/attr/Platform_Name'])
        info['resolution'] = dataset_id.resolution
        if var_name == 'pixel_longitude':
            info['standard_name'] = 'longitude'
        elif var_name == 'pixel_latitude':
            info['standard_name'] = 'latitude'

        return info
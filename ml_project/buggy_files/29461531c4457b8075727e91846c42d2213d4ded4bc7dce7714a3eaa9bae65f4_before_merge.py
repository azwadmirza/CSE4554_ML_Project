    def get_metadata(self, dataset_id, ds_info):
        var_name = ds_info.get('file_key', dataset_id.name)
        i = {}
        i.update(ds_info)
        for a in ['standard_name', 'units', 'long_name', 'flag_meanings', 'flag_values', 'flag_masks']:
            attr_path = var_name + '/attr/' + a
            if attr_path in self:
                i[a] = self[attr_path]

        u = i.get('units')
        if u in CF_UNITS:
            # CF compliance
            i['units'] = CF_UNITS[u]

        i['sensor'] = self.get_sensor(self['/attr/Sensor_Name'])
        i['platform'] = self.get_platform(self['/attr/Platform_Name'])
        i['resolution'] = dataset_id.resolution
        if var_name == 'pixel_longitude':
            i['standard_name'] = 'longitude'
        elif var_name == 'pixel_latitude':
            i['standard_name'] = 'latitude'

        return i
    def get_metadata(self, ds_id, ds_info):
        var_path = ds_info['file_key']
        info = getattr(self[var_path], 'attrs', {})
        info.update(ds_info)
        info.update({
            "shape": self.get_shape(ds_id, ds_info),
            "units": self[var_path + "/attr/UNIT"],
            "platform": self["/attr/PlatformShortName"].item(),
            "sensor": self["/attr/SensorShortName"].item(),
            "start_orbit": int(self["/attr/StartOrbitNumber"].item()),
            "end_orbit": int(self["/attr/StopOrbitNumber"].item()),
        })
        info.update(ds_id.to_dict())
        return info
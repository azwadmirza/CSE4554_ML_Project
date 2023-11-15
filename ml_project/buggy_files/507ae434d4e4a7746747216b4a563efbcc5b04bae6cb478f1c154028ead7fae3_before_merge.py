    def get_dataset(self, ds_id, ds_info, out=None):
        """Get output data and metadata of specified dataset"""
        var_path = ds_info['file_key']
        fill_value = ds_info.get('fill_value', 65535)
        dtype = ds_info.get('dtype', np.float32)

        if out is None:
            shape = self.get_shape(ds_id, ds_info)
            out = np.ma.empty(shape, dtype=dtype)
            out.mask = np.zeros(shape, dtype=np.bool)

        data = self[var_path]
        if ((ds_info.get('standard_name') == "longitude" or
             ds_info.get('standard_name') == "latitude") and
                ds_id.resolution == 10000):
            # FIXME: Lower frequency channels need CoRegistration parameters
            # applied
            out.mask[:] = data[:, ::2] == fill_value
            out.data[:] = data[:, ::2].astype(dtype) * self[var_path + "/attr/SCALE FACTOR"]
        else:
            out.mask[:] = data == fill_value
            out.data[:] = data.astype(dtype) * self[var_path + "/attr/SCALE FACTOR"]

        i = getattr(out, 'info', {})
        i.update(ds_info)
        i.update({
            "units": self[var_path + "/attr/UNIT"],
            "platform": self["/attr/PlatformShortName"].item(),
            "sensor": self["/attr/SensorShortName"].item(),
            "start_orbit": int(self["/attr/StartOrbitNumber"].item()),
            "end_orbit": int(self["/attr/StopOrbitNumber"].item()),
        })
        i.update(ds_id.to_dict())
        cls = ds_info.pop("container", Dataset)
        return cls(out.data, mask=out.mask, copy=False, **i)
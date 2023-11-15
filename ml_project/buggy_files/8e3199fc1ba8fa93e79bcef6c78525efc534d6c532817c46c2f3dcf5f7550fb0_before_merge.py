    def _get_calibration_params(self):
        """Get the calibration parameters from the metadata."""
        params = {}
        idx_table = []
        val_table = []
        for elt in self.mda['image_data_function'].split('\r\n'):
            try:
                key, val = elt.split(':=')
                try:
                    idx_table.append(int(key))
                    val_table.append(float(val))
                except ValueError:
                    params[key] = val
            except ValueError:
                pass
        params['indices'] = np.array(idx_table)
        params['values'] = np.array(val_table, dtype=np.float32)
        return params
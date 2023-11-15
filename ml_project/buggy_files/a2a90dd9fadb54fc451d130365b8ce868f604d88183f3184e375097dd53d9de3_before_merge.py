            def format_array(key, field):
                """internal helper to foramt array information for printing"""
                arr = get_scalar(self, key, preference=field)
                dl, dh = self.get_data_range(key)
                dl = pyvista.FLOAT_FORMAT.format(dl)
                dh = pyvista.FLOAT_FORMAT.format(dh)
                if key == self.active_scalar_info[1]:
                    key = '<b>{}</b>'.format(key)
                if arr.ndim > 1:
                    ncomp = arr.shape[1]
                else:
                    ncomp = 1
                return row.format(key, field, arr.dtype, ncomp, dl, dh)
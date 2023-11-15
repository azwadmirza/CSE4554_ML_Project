        def _deposit_field(field, data):
            """
            Create a grid field for particle quantities using given method.
            """
            pos = data[ptype, "particle_position"]
            if method == 'weighted_mean':
                d = data.ds.arr(data.deposit(pos, [data[ptype, deposit_field],
                                                   data[ptype, weight_field]],
                                             method=method, kernel_name=kernel_name),
                                             input_units=units)
                d[np.isnan(d)] = 0.0
            else:
                d = data.ds.arr(data.deposit(pos, [data[ptype, deposit_field]],
                                             method=method, kernel_name=kernel_name),
                                             input_units=units)
            return d
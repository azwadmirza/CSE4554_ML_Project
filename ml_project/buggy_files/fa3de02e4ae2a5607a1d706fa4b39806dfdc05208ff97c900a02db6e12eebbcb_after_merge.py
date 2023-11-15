        def _deposit_field(field, data):
            """
            Create a grid field for particle quantities using given method.
            """
            pos = data[ptype, "particle_position"]
            fields = [data[ptype, deposit_field]]
            if method == 'weighted_mean':
                fields.append(data[ptype, weight_field])
            fields = [np.ascontiguousarray(f) for f in fields]
            d = data.deposit(pos, fields, method=method,
                             kernel_name=kernel_name)
            d = data.ds.arr(d, input_units=units)
            if method == 'weighted_mean':
                d[np.isnan(d)] = 0.0
            return d
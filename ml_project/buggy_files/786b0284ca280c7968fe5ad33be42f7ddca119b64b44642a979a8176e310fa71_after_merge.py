    def _oblique_pixelize(self, data_source, field, bounds, size, antialias):
        indices = np.argsort(data_source['pdx'])[::-1].astype(np.int_)
        buff = np.zeros((size[1], size[0]), dtype="f8")
        pixelize_off_axis_cartesian(buff,
                              data_source['x'], data_source['y'],
                              data_source['z'], data_source['px'],
                              data_source['py'], data_source['pdx'],
                              data_source['pdy'], data_source['pdz'],
                              data_source.center, data_source._inv_mat, indices,
                              data_source[field], bounds)
        return buff
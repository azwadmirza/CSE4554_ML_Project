    def write_hdf5(self, filename, dataset_name=None, info=None, group_name=None):
        r"""Writes a YTArray to hdf5 file.

        Parameters
        ----------
        filename: string
            The filename to create and write a dataset to

        dataset_name: string
            The name of the dataset to create in the file.

        info: dictionary
            A dictionary of supplementary info to write to append as attributes
            to the dataset.

        group_name: string
            An optional group to write the arrays to. If not specified, the arrays
            are datasets at the top level by default.

        Examples
        --------
        >>> a = YTArray([1,2,3], 'cm')
        >>> myinfo = {'field':'dinosaurs', 'type':'field_data'}
        >>> a.write_hdf5('test_array_data.h5', dataset_name='dinosaurs',
        ...              info=myinfo)
        """
        from yt.extern.six.moves import cPickle as pickle
        if info is None:
            info = {}

        info['units'] = str(self.units)
        info['unit_registry'] = np.void(pickle.dumps(self.units.registry.lut))

        if dataset_name is None:
            dataset_name = 'array_data'

        f = h5py.File(filename, "w")
        if group_name is not None:
            if group_name in f:
                g = f[group_name]
            else:
                g = f.create_group(group_name)
        else:
            g = f
        if dataset_name in g.keys():
            d = g[dataset_name]
            # Overwrite without deleting if we can get away with it.
            if d.shape == self.shape and d.dtype == self.dtype:
                d[...] = self
                for k in d.attrs.keys():
                    del d.attrs[k]
            else:
                del f[dataset_name]
                d = g.create_dataset(dataset_name, data=self)
        else:
            d = g.create_dataset(dataset_name, data=self)

        for k, v in info.items():
            d.attrs[k] = v
        f.close()
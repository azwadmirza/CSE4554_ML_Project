    def save_datasets(self, datasets, filename, **kwargs):
        """Save all datasets to one or more files."""
        LOG.info('Saving datasets to NetCDF4/CF.')

        ds_collection = {}
        for ds in datasets:
            ds_collection.update(get_extra_ds(ds))

        datas = {}
        for ds in ds_collection.values():
            try:
                new_datasets = area2cf(ds)
            except KeyError:
                new_datasets = [ds]
            for new_ds in new_datasets:
                datas[new_ds.attrs['name']] = self.da2cf(new_ds,
                                                         kwargs.get('epoch',
                                                                    EPOCH))

        dataset = xr.Dataset(datas)
        dataset.attrs['history'] = ("Created by pytroll/satpy on " +
                                    str(datetime.utcnow()))
        dataset.attrs['conventions'] = 'CF-1.7'
        dataset.to_netcdf(filename, engine='h5netcdf')
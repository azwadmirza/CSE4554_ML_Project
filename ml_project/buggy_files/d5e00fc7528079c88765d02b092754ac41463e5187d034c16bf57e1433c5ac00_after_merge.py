    def save_datasets(self, datasets, filename, **kwargs):
        """Save all datasets to one or more files."""
        logger.info('Saving datasets to NetCDF4/CF.')

        datas, start_times, end_times = self._collect_datasets(datasets, kwargs)

        dataset = xr.Dataset(datas)
        try:
            dataset['time_bnds'] = make_time_bounds(dataset,
                                                    start_times,
                                                    end_times)
            dataset['time'].attrs['bounds'] = "time_bnds"
        except KeyError:
            logger.warning('No time dimension in datasets, skipping time bounds creation.')

        header_attrs = kwargs.pop('header_attrs', None)

        if header_attrs is not None:
            dataset.attrs.update({k: v for k, v in header_attrs.items() if v})

        dataset.attrs['history'] = ("Created by pytroll/satpy on " +
                                    str(datetime.utcnow()))
        dataset.attrs['conventions'] = 'CF-1.7'
        engine = kwargs.pop("engine", 'h5netcdf')
        kwargs.pop('config_files')
        kwargs.pop('compute')
        kwargs.pop('overlay', None)
        dataset.to_netcdf(filename, engine=engine, **kwargs)
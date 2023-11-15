    def _load_dataset_data(self,
                           file_handlers,
                           dsid,
                           xslice=slice(None),
                           yslice=slice(None)):
        ds_info = self.ids[dsid]
        proj = self._load_dataset(dsid, ds_info, file_handlers)
        # FIXME: areas could be concatenated here
        # Update the metadata
        proj.attrs['start_time'] = file_handlers[0].start_time
        proj.attrs['end_time'] = file_handlers[-1].end_time

        return proj
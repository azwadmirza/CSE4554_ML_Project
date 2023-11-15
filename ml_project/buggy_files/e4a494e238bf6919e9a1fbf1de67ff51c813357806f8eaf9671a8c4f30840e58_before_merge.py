    def _load_dataset_data(self,
                           file_handlers,
                           dsid,
                           xslice=slice(None),
                           yslice=slice(None)):
        ds_info = self.ids[dsid]
        try:
            # Can we allow the file handlers to do inplace data writes?
            [list(fhd.get_shape(dsid, ds_info)) for fhd in file_handlers]
        except NotImplementedError:
            # FIXME: Is NotImplementedError included in Exception for all
            # versions of Python?
            proj = self._load_entire_dataset(dsid, ds_info, file_handlers)
        else:
            proj = self._load_sliced_dataset(dsid, ds_info, file_handlers,
                                             xslice, yslice)
        # FIXME: areas could be concatenated here
        # Update the metadata
        proj.info['start_time'] = file_handlers[0].start_time
        proj.info['end_time'] = file_handlers[-1].end_time

        return proj
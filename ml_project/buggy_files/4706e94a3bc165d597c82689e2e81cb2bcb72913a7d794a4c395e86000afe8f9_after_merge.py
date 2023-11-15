    def load(self, dataset_keys, previous_datasets=None):
        """Load `dataset_keys`.

        If `previous_datasets` is provided, do not reload those."""
        all_datasets = previous_datasets or DatasetDict()
        datasets = DatasetDict()

        # Include coordinates in the list of datasets to load
        dsids = [self.get_dataset_key(ds_key) for ds_key in dataset_keys]
        coordinates = self._get_coordinates_for_dataset_keys(dsids)
        all_dsids = list(set().union(*coordinates.values())) + dsids

        for dsid in all_dsids:
            if dsid in all_datasets:
                continue
            coords = [all_datasets.get(cid, None)
                      for cid in coordinates.get(dsid, [])]
            ds = self._load_dataset_with_area(dsid, coords)
            if ds is not None:
                all_datasets[dsid] = ds
                if dsid in dsids:
                    datasets[dsid] = ds
        self._load_ancillary_variables(all_datasets)

        return datasets
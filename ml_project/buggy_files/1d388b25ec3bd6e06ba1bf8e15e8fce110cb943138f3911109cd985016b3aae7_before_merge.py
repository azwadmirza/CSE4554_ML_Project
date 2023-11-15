    def _dataset_wrapper(self, dataset, dataset_paths, **kwargs):
        wrapper_kwds = kwargs.copy()
        if dataset:
            real_path = dataset.file_name
            if real_path in dataset_paths:
                wrapper_kwds["dataset_path"] = dataset_paths[real_path]
        return DatasetFilenameWrapper(dataset, **wrapper_kwds)
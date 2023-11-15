    def update_cells(self, subset_cells):
        new_n_cells = len(subset_cells) if subset_cells.dtype is not np.dtype('bool') else subset_cells.sum()
        print("Downsampling from %i to %i cells" % (len(self), new_n_cells))
        for attr_name in ['_X', 'labels', 'batch_indices', 'local_means', 'local_vars']:
            setattr(self, attr_name, getattr(self, attr_name)[subset_cells])
        self.library_size_batch()
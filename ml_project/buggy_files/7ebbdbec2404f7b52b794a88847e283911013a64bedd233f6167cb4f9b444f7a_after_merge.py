    def add_data(self, gdf):
        # Populate columns idxs
        if not self.col_idx:
            for i, x in enumerate(gdf.columns.values):
                self.col_idx[str(x)] = i

        # list columns in cudf don't currently support chunked writing in parquet.
        # hack around this by just writing a single file with this partition
        # this restriction can be removed once cudf supports chunked writing
        # in parquet
        if any(is_list_dtype(gdf[col].dtype) for col in gdf.columns):
            self._write_table(0, gdf, True)
            return

        # Generate `ind` array to map each row to an output file.
        # This approach is certainly more optimized for shuffling
        # than it is for non-shuffling, but using a single code
        # path is probably worth the (possible) minor overhead.
        nrows = gdf.shape[0]
        typ = np.min_scalar_type(nrows * 2)
        if self.shuffle:
            ind = cp.random.choice(cp.arange(self.num_out_files, dtype=typ), nrows)
        else:
            ind = cp.arange(nrows, dtype=typ)
            cp.floor_divide(ind, math.ceil(nrows / self.num_out_files), out=ind)
        for x, group in enumerate(
            gdf.scatter_by_map(ind, map_size=self.num_out_files, keep_index=False)
        ):
            self.num_samples[x] += len(group)
            if self.num_threads > 1:
                self.queue.put((x, group))
            else:
                self._write_table(x, group)

        # wait for all writes to finish before exiting
        # (so that we aren't using memory)
        if self.num_threads > 1:
            self.queue.join()
    def data(self, data: Union[list, np.ndarray]):
        """ set the vertex data and build the vispy arrays for display """

        # convert data to a numpy array if it is not already one
        data = np.asarray(data)

        # Sort data by ID then time
        self._order = np.lexsort((data[:, 1], data[:, 0]))
        data = data[self._order]

        # check check the formatting of the incoming track data
        self._data = self._validate_track_data(data)

        # build the indices for sorting points by time
        self._ordered_points_idx = np.argsort(self.data[:, 1])
        self._points = self.data[self._ordered_points_idx, 1:]

        # build a tree of the track data to allow fast lookup of nearest track
        self._kdtree = cKDTree(self._points)

        # make the lookup table
        # NOTE(arl): it's important to convert the time index to an integer
        # here to make sure that we align with the napari dims index which
        # will be an integer - however, the time index does not necessarily
        # need to be an int, and the shader will render correctly.
        frames = list(set(self._points[:, 0].astype(np.uint).tolist()))
        self._points_lookup = [None] * (max(frames) + 1)
        for f in frames:
            idx = np.where(self._points[:, 0] == f)[0]
            self._points_lookup[f] = slice(min(idx), max(idx) + 1, 1)

        # make a second lookup table using a sparse matrix to convert track id
        # to the vertex indices
        self._id2idxs = coo_matrix(
            (
                np.broadcast_to(1, self.track_ids.size),  # just dummy ones
                (self.track_ids, np.arange(self.track_ids.size)),
            )
        ).tocsr()
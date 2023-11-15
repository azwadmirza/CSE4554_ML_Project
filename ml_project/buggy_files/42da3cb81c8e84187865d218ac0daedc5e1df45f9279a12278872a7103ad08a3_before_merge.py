    def query(self, keys: 'np.ndarray', top_k: int, *args, **kwargs) -> Tuple['np.ndarray', 'np.ndarray']:
        """ Find the top-k vectors with smallest ``metric`` and return their ids in ascending order.

        :return: a tuple of two ndarray.
            The first is ids in shape B x K (`dtype=int`), the second is metric in shape B x K (`dtype=float`)

        .. warning::
            This operation is memory-consuming.

            Distance (the smaller the better) is returned, not the score.

        """
        if self.metric not in {'cosine', 'euclidean'} or self.backend == 'scipy':
            dist = self._cdist(keys, self.query_handler)
        elif self.metric == 'euclidean':
            _keys = _ext_A(keys)
            dist = self._euclidean(_keys, self.query_handler)
        elif self.metric == 'cosine':
            _keys = _ext_A(_norm(keys))
            dist = self._cosine(_keys, self.query_handler)
        else:
            raise NotImplementedError(f'{self.metric} is not implemented')

        idx, dist = self._get_sorted_top_k(dist, top_k)
        return self.int2ext_id[idx], dist
    def _gen_reshape_rechunk_nsplits(old_shape, new_shape, nsplits):
        old_idx = len(old_shape) - 1
        new_idx = len(new_shape) - 1
        rechunk_nsplists = [None for _ in old_shape]
        reshape_nsplists = [None for _ in new_shape]

        while old_idx >= 0 or new_idx >= 0:
            old_dim_size = old_shape[old_idx]
            new_dim_size = new_shape[new_idx]

            if old_dim_size == new_dim_size:
                # nothing need to do
                rechunk_nsplists[old_idx] = nsplits[old_idx]
                reshape_nsplists[new_idx] = nsplits[old_idx]
                old_idx -= 1
                new_idx -= 1
                continue

            if old_dim_size == 1:
                rechunk_nsplists[old_idx] = (1,)
                old_idx -= 1
            elif new_dim_size == 1:
                reshape_nsplists[new_idx] = (1,)
                new_idx -= 1
            elif old_dim_size < new_dim_size:
                left_old_idx = old_idx - 1
                while left_old_idx >= 0 and \
                        np.prod(old_shape[left_old_idx: old_idx + 1]) < new_dim_size:
                    left_old_idx -= 1
                if np.prod(old_shape[left_old_idx: old_idx + 1]) != new_dim_size:
                    raise ValueError('shapes not compatible')

                for i in range(left_old_idx + 1, old_idx + 1):
                    # rechunk the higher dimension into 1 chunk
                    # e.g. ((2, 2, 2), [(3, 3), (4, 4))] -> [6, 8]
                    rechunk_nsplists[i] = (old_shape[i],)

                chunk_reduce = np.prod([len(c) for c in nsplits[left_old_idx + 1: old_idx + 1]])
                # cause the higher dimension has been concatenated,
                # the lowest dimension should be expanded to reduce size
                rechunk_nsplists[left_old_idx] = \
                    TensorReshape._expand_nsplit_by_reduce(nsplits[left_old_idx], chunk_reduce)

                size_reduce = np.prod(old_shape[left_old_idx + 1: old_idx + 1])
                reshape_nsplists[new_idx] = tuple(size_reduce * c for c in rechunk_nsplists[left_old_idx])

                old_idx = left_old_idx - 1
                new_idx -= 1
            else:
                assert old_dim_size > new_dim_size
                lef_new_idx = new_idx - 1
                while lef_new_idx >= 0 and \
                        np.prod(new_shape[lef_new_idx: new_idx + 1]) < old_dim_size:
                    lef_new_idx -= 1
                if np.prod(new_shape[lef_new_idx: new_idx + 1]) != old_dim_size:
                    raise ValueError('shapes not compatible')

                chunk_expand = np.prod(new_shape[lef_new_idx + 1: new_idx + 1])
                rechunk_nsplists[old_idx] = TensorReshape._reduce_nsplit_by_expand(nsplits[old_idx], chunk_expand)

                for i in range(lef_new_idx + 1, new_idx + 1):
                    reshape_nsplists[i] = (new_shape[i],)
                reshape_nsplists[lef_new_idx] = tuple(c // chunk_expand for c in rechunk_nsplists[old_idx])

                old_idx -= 1
                new_idx = lef_new_idx - 1

        assert np.prod([len(s) for s in rechunk_nsplists]) == \
               np.prod([len(s) for s in reshape_nsplists])
        return rechunk_nsplists, reshape_nsplists
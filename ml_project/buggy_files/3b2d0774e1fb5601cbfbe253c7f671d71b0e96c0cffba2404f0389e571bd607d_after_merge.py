    def size(self):
        """
        Compute group sizes

        """
        ids, _, ngroup = self.group_info
        ids = com._ensure_platform_int(ids)
        out = np.bincount(ids[ids != -1], minlength=ngroup)
        return Series(out, index=self.result_index, dtype='int64')
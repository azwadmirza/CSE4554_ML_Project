    def _transform_fast(self, func):
        """
        fast version of transform, only applicable to
        builtin/cythonizable functions
        """
        if isinstance(func, compat.string_types):
            func = getattr(self, func)

        ids, _, ngroup = self.grouper.group_info
        mask = ids != -1

        out = func().values[ids]
        if not mask.all():
            out = np.where(mask, out, np.nan)

        obs = np.zeros(ngroup, dtype='bool')
        obs[ids[mask]] = True
        if not obs.all():
            out = self._try_cast(out, self._selected_obj)

        return Series(out, index=self.obj.index)
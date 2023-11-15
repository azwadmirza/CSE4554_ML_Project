    def __getitem__(self, indx):
        """
        Get the index.

        """
        m = self._mask
        if isinstance(m[indx], ndarray):
            # Can happen when indx is a multi-dimensional field:
            # A = ma.masked_array(data=[([0,1],)], mask=[([True,
            #                     False],)], dtype=[("A", ">i2", (2,))])
            # x = A[0]; y = x["A"]; then y.mask["A"].size==2
            # and we can not say masked/unmasked.
            # The result is no longer mvoid!
            # See also issue #6724.
            return masked_array(
                data=self._data[indx], mask=m[indx],
                fill_value=self._fill_value[indx],
                hard_mask=self._hardmask)
        if m is not nomask and m[indx]:
            return masked
        return self._data[indx]
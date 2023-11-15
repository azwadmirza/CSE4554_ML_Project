    def squeeze(self, ndim=0, axis=None):
        to_squeeze = self.to_pandas()
        # This is the case for 1xN or Nx1 DF - Need to call squeeze
        if ndim == 1:
            if axis is None:
                axis = 0 if self.data.shape[1] > 1 else 1
            squeezed = pandas.Series(to_squeeze.squeeze())
            # In the case of `MultiIndex`, we already have the correct index and naming
            # because we are going from pandas above. This step is to correct the
            # `Series` to have the correct name and index.
            if not isinstance(squeezed.index, pandas.MultiIndex):
                scaler_axis = self.columns if axis else self.index
                non_scaler_axis = self.index if axis else self.columns
                squeezed.name = scaler_axis[0]
                squeezed.index = non_scaler_axis
            return squeezed
        # This is the case for a 1x1 DF - We don't need to squeeze
        else:
            return to_squeeze.values[0][0]
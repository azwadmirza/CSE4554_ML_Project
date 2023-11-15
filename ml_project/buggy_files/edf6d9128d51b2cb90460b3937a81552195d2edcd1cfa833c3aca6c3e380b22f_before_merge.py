    def squeeze(self, ndim=0, axis=None):
        to_squeeze = self.data.to_pandas()
        # This is the case for 1xN or Nx1 DF - Need to call squeeze
        if ndim == 1:
            if axis is None:
                axis = 0 if self.data.shape[1] > 1 else 1
            squeezed = pandas.Series(to_squeeze.squeeze(axis))
            scaler_axis = self.columns if axis else self.index
            non_scaler_axis = self.index if axis else self.columns
            squeezed.name = scaler_axis[0]
            squeezed.index = non_scaler_axis
            return squeezed
        # This is the case for a 1x1 DF - We don't need to squeeze
        else:
            return to_squeeze.values[0][0]
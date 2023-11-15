    def _wrap_data(self, data, start_idx, end_idx, names=None):
        # TODO: check if this is reasonable for statespace
        # squeezing data: data may be:
        # - m x n: m dates, n simulations -> squeeze does nothing
        # - m x 1: m dates, 1 simulation -> squeeze removes last dimension
        # - 1 x n: don't squeeze, already fine
        # - 1 x 1: squeeze only second axis
        if data.ndim > 1 and data.shape[1] == 1:
            data = np.squeeze(data, axis=1)
        data = np.squeeze(data)
        if self.use_pandas:
            _, _, _, index = self._get_prediction_index(start_idx, end_idx)
            if data.ndim < 2:
                data = pd.Series(data, index=index, name=names)
            else:
                data = pd.DataFrame(data, index=index, columns=names)
        return data
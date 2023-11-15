    def _transform(self, y, X=None):
        """Transform data using rolling window approach"""
        if X is not None:
            raise NotImplementedError()
        y = check_y(y)

        # get integer time index
        cv = self._cv

        # Transform target series into tabular format using
        # rolling window tabularisation
        x_windows = []
        y_windows = []
        for x_index, y_index in cv.split(y):
            x_window = y.iloc[x_index]
            y_window = y.iloc[y_index]

            x_windows.append(x_window)
            y_windows.append(y_window)

        # Put into required input format for regression
        X, y = self._format_windows(x_windows, y_windows)
        return X, y
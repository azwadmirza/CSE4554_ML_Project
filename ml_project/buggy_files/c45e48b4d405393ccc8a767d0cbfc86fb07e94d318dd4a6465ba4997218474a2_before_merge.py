    def _transform(self, y_train, X_train=None):
        """Transform data using rolling window approach"""
        if X_train is not None:
            raise NotImplementedError()
        y_train = check_y(y_train)

        # get integer time index
        cv = self._cv

        # Transform target series into tabular format using
        # rolling window tabularisation
        x_windows = []
        y_windows = []
        for x_index, y_index in cv.split(y_train):
            x_window = y_train.iloc[x_index]
            y_window = y_train.iloc[y_index]

            x_windows.append(x_window)
            y_windows.append(y_window)

        # Put into required input format for regression
        X_train, y_train = self._format_windows(x_windows, y_windows)
        return X_train, y_train
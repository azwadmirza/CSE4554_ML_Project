    def transform(self, T):
        """Transform new data by linear interpolation

        Parameters
        ----------
        T : array-like, shape=(n_samples,)
            Data to transform.

        Returns
        -------
        `T_` : array, shape=(n_samples,)
            The transformed data
        """
        T = as_float_array(T)
        if len(T.shape) != 1:
            raise ValueError("X should be a vector")

        # Handle the out_of_bounds argument by setting bounds_error and T
        if self.out_of_bounds == "raise":
            f = interpolate.interp1d(self.X_, self.y_, kind='linear',
                                     bounds_error=True)
        elif self.out_of_bounds == "nan":
            f = interpolate.interp1d(self.X_, self.y_, kind='linear',
                                     bounds_error=False)
        elif self.out_of_bounds == "clip":
            f = interpolate.interp1d(self.X_, self.y_, kind='linear',
                                     bounds_error=False)
            T = np.clip(T, self.X_min_, self.X_max_)
        else:
            raise ValueError("The argument ``out_of_bounds`` must be in "
                             "'nan', 'clip', 'raise'; got {0}"
                             .format(self.out_of_bounds))

        return f(T)
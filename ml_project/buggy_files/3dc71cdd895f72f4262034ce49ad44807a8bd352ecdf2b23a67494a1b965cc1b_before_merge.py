    def estimate_parameters(self, signal, x1, x2, only_current=False):
        """Estimate the parameters by the two area method

        Parameters
        ----------
        signal : Signal instance
        x1 : float
            Defines the left limit of the spectral range to use for the
            estimation.
        x2 : float
            Defines the right limit of the spectral range to use for the
            estimation.

        only_current : bool
            If False estimates the parameters for the full dataset.

        Returns
        -------
        bool

        """
        axis = signal.axes_manager.signal_axes[0]
        binned = signal.metadata.Signal.binned
        i1, i2 = axis.value_range_to_indices(x1, x2)
        if only_current is True:
            estimation = np.polyfit(axis.axis[i1:i2],
                                    signal()[i1:i2],
                                    self.get_polynomial_order())
            if binned is True:
                self.coefficients.value = estimation / axis.scale
            else:
                self.coefficients.value = estimation
            return True
        else:
            if self.coefficients.map is None:
                self._create_arrays()
            nav_shape = signal.axes_manager._navigation_shape_in_array
            signal.unfold()
            dc = signal.data
            # For polyfit the spectrum goes in the first axis
            if axis.index_in_array > 0:
                dc = np.rollaxis(dc, axis.index_in_array, 0)
            cmaps = np.polyfit(axis.axis[i1:i2],
                               dc[i1:i2, :], self.get_polynomial_order()).reshape([
                                   self.get_polynomial_order() + 1, ] + nav_shape)
            self.coefficients.map['values'][:] = np.rollaxis(cmaps, 0,
                                                             axis.index_in_array)
            if binned is True:
                self.coefficients.map["values"] /= axis.scale
            self.coefficients.map['is_set'][:] = True
            signal.fold()
            self.fetch_stored_values()
            return True
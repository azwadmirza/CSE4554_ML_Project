    def estimate_shift1D(self,
                         start=None,
                         end=None,
                         reference_indices=None,
                         max_shift=None,
                         interpolate=True,
                         number_of_interpolation_points=5,
                         mask=None,
                         parallel=None,
                         show_progressbar=None):
        """Estimate the shifts in the current signal axis using
         cross-correlation.
        This method can only estimate the shift by comparing
        unidimensional features that should not change the position in
        the signal axis. To decrease the memory usage, the time of
        computation and the accuracy of the results it is convenient to
        select the feature of interest providing sensible values for
        `start` and `end`. By default interpolation is used to obtain
        subpixel precision.
        Parameters
        ----------
        start, end : {int | float | None}
            The limits of the interval. If int they are taken as the
            axis index. If float they are taken as the axis value.
        reference_indices : tuple of ints or None
            Defines the coordinates of the spectrum that will be used
            as eference. If None the spectrum at the current
            coordinates is used for this purpose.
        max_shift : int
            "Saturation limit" for the shift.
        interpolate : bool
            If True, interpolation is used to provide sub-pixel
            accuracy.
        number_of_interpolation_points : int
            Number of interpolation points. Warning: making this number
            too big can saturate the memory
        mask : BaseSignal of bool data type.
            It must have signal_dimension = 0 and navigation_shape equal to the
            current signal. Where mask is True the shift is not computed
            and set to nan.
        parallel : {None, bool}
        show_progressbar : None or bool
            If True, display a progress bar. If None the default is set in
            `preferences`.
        Returns
        -------
        An array with the result of the estimation in the axis units.
        Raises
        ------
        SignalDimensionError if the signal dimension is not 1.
        """
        if show_progressbar is None:
            show_progressbar = preferences.General.show_progressbar
        self._check_signal_dimension_equals_one()
        ip = number_of_interpolation_points + 1
        axis = self.axes_manager.signal_axes[0]
        self._check_navigation_mask(mask)
        # we compute for now
        if isinstance(start, da.Array):
            start = start.compute()
        if isinstance(end, da.Array):
            end = end.compute()
        i1, i2 = axis._get_index(start), axis._get_index(end)
        if reference_indices is None:
            reference_indices = self.axes_manager.indices
        ref = self.inav[reference_indices].data[i1:i2]

        if interpolate is True:
            ref = interpolate1D(ip, ref)
        iterating_kwargs = ()
        if mask is not None:
            iterating_kwargs += (('mask', mask),)
        shift_signal = self._map_iterate(
            _estimate_shift1D,
            iterating_kwargs=iterating_kwargs,
            data_slice=slice(i1, i2),
            mask=None,
            ref=ref,
            ip=ip,
            interpolate=interpolate,
            ragged=False,
            parallel=parallel,
            inplace=False,
            show_progressbar=show_progressbar,)
        shift_array = shift_signal.data
        if max_shift is not None:
            if interpolate is True:
                max_shift *= ip
            shift_array.clip(-max_shift, max_shift)
        if interpolate is True:
            shift_array = shift_array / ip
        shift_array *= axis.scale
        return shift_array
    def align_zero_loss_peak(
            self,
            calibrate=True,
            also_align=[],
            print_stats=True,
            subpixel=True,
            mask=None,
            signal_range=None,
            show_progressbar=None,
            **kwargs):
        """Align the zero-loss peak.

        This function first aligns the spectra using the result of
        `estimate_zero_loss_peak_centre` and afterward, if subpixel is True,
        proceeds to align with subpixel accuracy using `align1D`. The offset
        is automatically correct if `calibrate` is True.

        Parameters
        ----------
        calibrate : bool
            If True, set the offset of the spectral axis so that the
            zero-loss peak is at position zero.
        also_align : list of signals
            A list containing other spectra of identical dimensions to
            align using the shifts applied to the current spectrum.
            If `calibrate` is True, the calibration is also applied to
            the spectra in the list.
        print_stats : bool
            If True, print summary statistics of the ZLP maximum before
            the aligment.
        subpixel : bool
            If True, perform the alignment with subpixel accuracy
            using cross-correlation.
        mask : Signal1D of bool data type.
            It must have signal_dimension = 0 and navigation_shape equal to the
            current signal. Where mask is True the shift is not computed
            and set to nan.
        signal_range : tuple of integers, tuple of floats. Optional
            Will only search for the ZLP within the signal_range. If given
            in integers, the range will be in index values. If given floats,
            the range will be in spectrum values. Useful if there are features
            in the spectrum which are more intense than the ZLP.
            Default is searching in the whole signal.
        show_progressbar : None or bool
            If True, display a progress bar. If None the default is set in
            `preferences`.

        Examples
        --------
        >>> s_ll = hs.signals.EELSSpectrum(np.zeros(1000))
        >>> s_ll.data[100] = 100
        >>> s_ll.align_zero_loss_peak()

        Aligning both the lowloss signal and another signal
        >>> s = hs.signals.EELSSpectrum(np.range(1000))
        >>> s_ll.align_zero_loss_peak(also_align=[s])

        Aligning within a narrow range of the lowloss signal
        >>> s_ll.align_zero_loss_peak(signal_range=(-10.,10.))


        See Also
        --------
        estimate_zero_loss_peak_centre, align1D, estimate_shift1D.

        Notes
        -----
        Any extra keyword arguments are passed to `align1D`. For
        more information read its docstring.

        """
        signal_range = signal_range_from_roi(signal_range)

        def substract_from_offset(value, signals):
            if isinstance(value, da.Array):
                value = value.compute()
            for signal in signals:
                signal.axes_manager[-1].offset -= value

        def estimate_zero_loss_peak_centre(s, mask, signal_range):
            if signal_range:
                zlpc = s.isig[signal_range[0]:signal_range[1]].\
                    estimate_zero_loss_peak_centre(mask=mask)
            else:
                zlpc = s.estimate_zero_loss_peak_centre(mask=mask)
            return zlpc

        zlpc = estimate_zero_loss_peak_centre(
            self, mask=mask, signal_range=signal_range)

        mean_ = np.nanmean(zlpc.data)

        if print_stats is True:
            print()
            print(underline("Initial ZLP position statistics"))
            zlpc.print_summary_statistics()

        for signal in also_align + [self]:
            shift_array = -zlpc.data + mean_
            if zlpc._lazy:
                shift_array = shift_array.compute()
            signal.shift1D(shift_array, show_progressbar=show_progressbar)

        if calibrate is True:
            zlpc = estimate_zero_loss_peak_centre(
                self, mask=mask, signal_range=signal_range)
            substract_from_offset(np.nanmean(zlpc.data),
                                  also_align + [self])

        if subpixel is False:
            return
        left, right = -3., 3.
        if calibrate is False:
            mean_ = np.nanmean(estimate_zero_loss_peak_centre(
                self, mask, signal_range).data)
            left += mean_
            right += mean_

        left = (left if left > self.axes_manager[-1].axis[0]
                else self.axes_manager[-1].axis[0])
        right = (right if right < self.axes_manager[-1].axis[-1]
                 else self.axes_manager[-1].axis[-1])

        if self.axes_manager.navigation_size > 1:
            self.align1D(
                left,
                right,
                also_align=also_align,
                show_progressbar=show_progressbar,
                mask=mask,
                **kwargs)
        if calibrate is True:
            zlpc = estimate_zero_loss_peak_centre(
                self, mask=mask, signal_range=signal_range)
            substract_from_offset(np.nanmean(zlpc.data),
                                  also_align + [self])
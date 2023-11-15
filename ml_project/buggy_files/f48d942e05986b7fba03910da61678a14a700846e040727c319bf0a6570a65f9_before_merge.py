    def get_lines_intensity(self,
                            xray_lines=None,
                            integration_windows=2.,
                            background_windows=None,
                            plot_result=False,
                            only_one=True,
                            only_lines=("a",),
                            **kwargs):
        """Return the intensity map of selected Xray lines.

        The intensities, the number of X-ray counts, are computed by
        suming the spectrum over the
        different X-ray lines. The sum window width
        is calculated from the energy resolution of the detector
        as defined in 'energy_resolution_MnKa' of the metadata.
        Backgrounds average in provided windows can be subtracted from the
        intensities.

        Parameters
        ----------
        xray_lines: {None, list of string}
            If None,
            if `metadata.Sample.elements.xray_lines` contains a
            list of lines use those.
            If `metadata.Sample.elements.xray_lines` is undefined
            or empty but `metadata.Sample.elements` is defined,
            use the same syntax as `add_line` to select a subset of lines
            for the operation.
            Alternatively, provide an iterable containing
            a list of valid X-ray lines symbols.
        integration_windows: Float or array
            If float, the width of the integration windows is the
            'integration_windows_width' times the calculated FWHM of the line.
            Else provide an array for which each row corresponds to a X-ray
            line. Each row contains the left and right value of the window.
        background_windows: None or 2D array of float
            If None, no background subtraction. Else, the backgrounds average
            in the windows are subtracted from the return intensities.
            'background_windows' provides the position of the windows in
            energy. Each line corresponds to a X-ray line. In a line, the two
            first values correspond to the limits of the left window and the
            two last values correspond to the limits of the right window.
        plot_result : bool
            If True, plot the calculated line intensities. If the current
            object is a single spectrum it prints the result instead.
        only_one : bool
            If False, use all the lines of each element in the data spectral
            range. If True use only the line at the highest energy
            above an overvoltage of 2 (< beam energy / 2).
        only_lines : {None, list of strings}
            If not None, use only the given lines.
        kwargs
            The extra keyword arguments for plotting. See
            `utils.plot.plot_signals`

        Returns
        -------
        intensities : list
            A list containing the intensities as BaseSignal subclasses.

        Examples
        --------
        >>> s = hs.datasets.example_signals.EDS_SEM_Spectrum()
        >>> s.get_lines_intensity(['Mn_Ka'], plot_result=True)
        Mn_La at 0.63316 keV : Intensity = 96700.00

        >>> s = hs.datasets.example_signals.EDS_SEM_Spectrum()
        >>> s.plot(['Mn_Ka'], integration_windows=2.1)
        >>> s.get_lines_intensity(['Mn_Ka'],
        >>>                       integration_windows=2.1, plot_result=True)
        Mn_Ka at 5.8987 keV : Intensity = 53597.00

        >>> s = hs.datasets.example_signals.EDS_SEM_Spectrum()
        >>> s.set_elements(['Mn'])
        >>> s.set_lines(['Mn_Ka'])
        >>> bw = s.estimate_background_windows()
        >>> s.plot(background_windows=bw)
        >>> s.get_lines_intensity(background_windows=bw, plot_result=True)
        Mn_Ka at 5.8987 keV : Intensity = 46716.00

        See also
        --------
        set_elements, add_elements, estimate_background_windows,
        plot

        """

        xray_lines = self._parse_xray_lines(xray_lines, only_one, only_lines)
        if hasattr(integration_windows, '__iter__') is False:
            integration_windows = self.estimate_integration_windows(
                windows_width=integration_windows, xray_lines=xray_lines)
        intensities = []
        ax = self.axes_manager.signal_axes[0]
        # test Signal1D (0D problem)
        # signal_to_index = self.axes_manager.navigation_dimension - 2
        for i, (Xray_line, window) in enumerate(
                zip(xray_lines, integration_windows)):
            element, line = utils_eds._get_element_and_line(Xray_line)
            line_energy = self._get_line_energy(Xray_line)
            img = self.isig[window[0]:window[1]].integrate1D(-1)
            if np.issubdtype(img.data.dtype, np.integer):
                # The operations below require a float dtype with the default
                # numpy casting rule ('same_kind')
                img.change_dtype("float")
            if background_windows is not None:
                bw = background_windows[i]
                # TODO: test to prevent slicing bug. To be reomved when fixed
                indexes = [float(ax.value2index(de))
                           for de in list(bw) + window]
                if indexes[0] == indexes[1]:
                    bck1 = self.isig[bw[0]]
                else:
                    bck1 = self.isig[bw[0]:bw[1]].integrate1D(-1)
                if indexes[2] == indexes[3]:
                    bck2 = self.isig[bw[2]]
                else:
                    bck2 = self.isig[bw[2]:bw[3]].integrate1D(-1)
                corr_factor = (indexes[5] - indexes[4]) / (
                    (indexes[1] - indexes[0]) + (indexes[3] - indexes[2]))
                img = img - (bck1 + bck2) * corr_factor
            img.metadata.General.title = (
                'X-ray line intensity of %s: %s at %.2f %s' %
                (self.metadata.General.title,
                 Xray_line,
                 line_energy,
                 self.axes_manager.signal_axes[0].units,
                 ))
            img.axes_manager.set_signal_dimension(0)
            if plot_result and img.axes_manager.navigation_size == 1:
                print("%s at %s %s : Intensity = %.2f"
                      % (Xray_line,
                         line_energy,
                         ax.units,
                         img.data))
            img.metadata.set_item("Sample.elements", ([element]))
            img.metadata.set_item("Sample.xray_lines", ([Xray_line]))
            intensities.append(img)
        if plot_result and img.axes_manager.navigation_size != 1:
            utils.plot.plot_signals(intensities, **kwargs)
        return intensities
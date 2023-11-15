    def kramers_kronig_analysis(self,
                                zlp=None,
                                iterations=1,
                                n=None,
                                t=None,
                                delta=0.5,
                                full_output=False):
        """Calculate the complex
        dielectric function from a single scattering distribution (SSD) using
        the Kramers-Kronig relations.

        It uses the FFT method as in [Egerton2011]_.  The SSD is an
        EELSSpectrum instance containing SSD low-loss EELS with no zero-loss
        peak. The internal loop is devised to approximately subtract the
        surface plasmon contribution supposing an unoxidized planar surface and
        neglecting coupling between the surfaces. This method does not account
        for retardation effects, instrumental broading and surface plasmon
        excitation in particles.

        Note that either refractive index or thickness are required.
        If both are None or if both are provided an exception is raised.

        Parameters
        ----------
        zlp: {None, number, Signal1D}
            ZLP intensity. It is optional (can be None) if `t` is None and `n`
            is not None and the thickness estimation is not required. If `t`
            is not None, the ZLP is required to perform the normalization and
            if `t` is not None, the ZLP is required to calculate the thickness.
            If the ZLP is the same for all spectra, the integral of the ZLP
            can be provided as a number. Otherwise, if the ZLP intensity is not
            the same for all spectra, it can be provided as i) a Signal1D
            of the same dimensions as the current signal containing the ZLP
            spectra for each location ii) a BaseSignal of signal dimension 0
            and navigation_dimension equal to the current signal containing the
            integrated ZLP intensity.
        iterations: int
            Number of the iterations for the internal loop to remove the
            surface plasmon contribution. If 1 the surface plasmon contribution
            is not estimated and subtracted (the default is 1).
        n: {None, float}
            The medium refractive index. Used for normalization of the
            SSD to obtain the energy loss function. If given the thickness
            is estimated and returned. It is only required when `t` is None.
        t: {None, number, Signal1D}
            The sample thickness in nm. Used for normalization of the
            SSD to obtain the energy loss function. It is only required when
            `n` is None. If the thickness is the same for all spectra it can be
            given by a number. Otherwise, it can be provided as a BaseSignal
            with signal dimension 0 and navigation_dimension equal to the
            current signal.
        delta : float
            A small number (0.1-0.5 eV) added to the energy axis in
            specific steps of the calculation the surface loss correction to
            improve stability.
        full_output : bool
            If True, return a dictionary that contains the estimated
            thickness if `t` is None and the estimated surface plasmon
            excitation and the spectrum corrected from surface plasmon
            excitations if `iterations` > 1.

        Returns
        -------
        eps: DielectricFunction instance
            The complex dielectric function results,
                $\epsilon = \epsilon_1 + i*\epsilon_2$,
            contained in an DielectricFunction instance.
        output: Dictionary (optional)
            A dictionary of optional outputs with the following keys:

            ``thickness``
                The estimated  thickness in nm calculated by normalization of
                the SSD (only when `t` is None)

            ``surface plasmon estimation``
               The estimated surface plasmon excitation (only if
               `iterations` > 1.)

        Raises
        ------
        ValuerError
            If both `n` and `t` are undefined (None).
        AttribureError
            If the beam_energy or the collection semi-angle are not defined in
            metadata.

        Notes
        -----
        This method is based in Egerton's Matlab code [Egerton2011]_ with some
        minor differences:

        * The integrals are performed using the simpsom rule instead of using
          a summation.
        * The wrap-around problem when computing the ffts is workarounded by
          padding the signal instead of substracting the reflected tail.

        .. [Egerton2011] Ray Egerton, "Electron Energy-Loss
           Spectroscopy in the Electron Microscope", Springer-Verlag, 2011.

        """
        output = {}
        if iterations == 1:
            # In this case s.data is not modified so there is no need to make
            # a deep copy.
            s = self.isig[0.:]
        else:
            s = self.isig[0.:].deepcopy()

        sorig = self.isig[0.:]
        # Avoid singularity at 0
        if s.axes_manager.signal_axes[0].axis[0] == 0:
            s = s.isig[1:]
            sorig = self.isig[1:]

        # Constants and units
        me = constants.value(
            'electron mass energy equivalent in MeV') * 1e3  # keV

        # Mapped parameters
        try:
            e0 = s.metadata.Acquisition_instrument.TEM.beam_energy
        except BaseException:
            raise AttributeError("Please define the beam energy."
                                 "You can do this e.g. by using the "
                                 "set_microscope_parameters method")
        try:
            beta = s.metadata.Acquisition_instrument.TEM.Detector.\
                EELS.collection_angle
        except BaseException:
            raise AttributeError("Please define the collection semi-angle. "
                                 "You can do this e.g. by using the "
                                 "set_microscope_parameters method")

        axis = s.axes_manager.signal_axes[0]
        eaxis = axis.axis.copy()

        if isinstance(zlp, hyperspy.signal.BaseSignal):
            if (zlp.axes_manager.navigation_dimension ==
                    self.axes_manager.navigation_dimension):
                if zlp.axes_manager.signal_dimension == 0:
                    i0 = zlp.data
                else:
                    i0 = zlp.integrate1D(axis.index_in_axes_manager).data
            else:
                raise ValueError('The ZLP signal dimensions are not '
                                 'compatible with the dimensions of the '
                                 'low-loss signal')
            # The following prevents errors if the signal is a single spectrum
            if len(i0) != 1:
                i0 = i0.reshape(
                    np.insert(i0.shape, axis.index_in_array, 1))
        elif isinstance(zlp, numbers.Number):
            i0 = zlp
        else:
            raise ValueError('The zero-loss peak input is not valid, it must be\
                             in the BaseSignal class or a Number.')

        if isinstance(t, hyperspy.signal.BaseSignal):
            if (t.axes_manager.navigation_dimension ==
                    self.axes_manager.navigation_dimension) and (
                    t.axes_manager.signal_dimension == 0):
                t = t.data
                t = t.reshape(
                    np.insert(t.shape, axis.index_in_array, 1))
            else:
                raise ValueError('The thickness signal dimensions are not '
                                 'compatible with the dimensions of the '
                                 'low-loss signal')
        elif isinstance(t, np.ndarray) and t.shape and t.shape != (1,):
            raise ValueError("thickness must be a HyperSpy signal or a number,"
                             " not a numpy array.")

        # Slicer to get the signal data from 0 to axis.size
        slicer = s.axes_manager._get_data_slice(
            [(axis.index_in_array, slice(None, axis.size)), ])

        # Kinetic definitions
        ke = e0 * (1 + e0 / 2. / me) / (1 + e0 / me) ** 2
        tgt = e0 * (2 * me + e0) / (me + e0)
        rk0 = 2590 * (1 + e0 / me) * np.sqrt(2 * ke / me)

        for io in range(iterations):
            # Calculation of the ELF by normalization of the SSD
            # Norm(SSD) = Imag(-1/epsilon) (Energy Loss Funtion, ELF)

            # We start by the "angular corrections"
            Im = s.data / (np.log(1 + (beta * tgt / eaxis) ** 2)) / axis.scale
            if n is None and t is None:
                raise ValueError("The thickness and the refractive index are "
                                 "not defined. Please provide one of them.")
            elif n is not None and t is not None:
                raise ValueError("Please provide the refractive index OR the "
                                 "thickness information, not both")
            elif n is not None:
                # normalize using the refractive index.
                K = (Im / eaxis).sum(axis=axis.index_in_array) * axis.scale
                K = (K / (np.pi / 2) / (1 - 1. / n ** 2)).reshape(
                    np.insert(K.shape, axis.index_in_array, 1))
                # Calculate the thickness only if possible and required
                if zlp is not None and (full_output is True or
                                        iterations > 1):
                    te = (332.5 * K * ke / i0)
                    if full_output is True:
                        output['thickness'] = te
            elif t is not None:
                if zlp is None:
                    raise ValueError("The ZLP must be provided when the  "
                                     "thickness is used for normalization.")
                # normalize using the thickness
                K = t * i0 / (332.5 * ke)
                te = t
            Im = Im / K

            # Kramers Kronig Transform:
            # We calculate KKT(Im(-1/epsilon))=1+Re(1/epsilon) with FFT
            # Follows: D W Johnson 1975 J. Phys. A: Math. Gen. 8 490
            # Use a size that is a power of two to speed up the fft and
            # make it double the closest upper value to workaround the
            # wrap-around problem.
            esize = 2 * closest_power_of_two(axis.size)
            q = -2 * np.fft.fft(Im, esize,
                                axis.index_in_array).imag / esize

            q[slicer] *= -1
            q = np.fft.fft(q, axis=axis.index_in_array)
            # Final touch, we have Re(1/eps)
            Re = q[slicer].real + 1

            # Egerton does this to correct the wrap-around problem, but in our
            # case this is not necessary because we compute the fft on an
            # extended and padded spectrum to avoid this problem.
            # Re=real(q)
            # Tail correction
            # vm=Re[axis.size-1]
            # Re[:(axis.size-1)]=Re[:(axis.size-1)]+1-(0.5*vm*((axis.size-1) /
            #  (axis.size*2-arange(0,axis.size-1)))**2)
            # Re[axis.size:]=1+(0.5*vm*((axis.size-1) /
            #  (axis.size+arange(0,axis.size)))**2)

            # Epsilon appears:
            #  We calculate the real and imaginary parts of the CDF
            e1 = Re / (Re ** 2 + Im ** 2)
            e2 = Im / (Re ** 2 + Im ** 2)

            if iterations > 1 and zlp is not None:
                # Surface losses correction:
                #  Calculates the surface ELF from a vaccumm border effect
                #  A simulated surface plasmon is subtracted from the ELF
                Srfelf = 4 * e2 / ((e1 + 1) ** 2 + e2 ** 2) - Im
                adep = (tgt / (eaxis + delta) *
                        np.arctan(beta * tgt / axis.axis) -
                        beta / 1000. /
                        (beta ** 2 + axis.axis ** 2. / tgt ** 2))
                Srfint = 2000 * K * adep * Srfelf / rk0 / te * axis.scale
                s.data = sorig.data - Srfint
                _logger.debug('Iteration number: %d / %d', io + 1, iterations)
                if iterations == io + 1 and full_output is True:
                    sp = sorig._deepcopy_with_new_data(Srfint)
                    sp.metadata.General.title += (
                        " estimated surface plasmon excitation.")
                    output['surface plasmon estimation'] = sp
                    del sp
                del Srfint

        eps = s._deepcopy_with_new_data(e1 + e2 * 1j)
        del s
        eps.set_signal_type("DielectricFunction")
        eps.metadata.General.title = (self.metadata.General.title +
                                      'dielectric function '
                                      '(from Kramers-Kronig analysis)')
        if eps.tmp_parameters.has_item('filename'):
            eps.tmp_parameters.filename = (
                self.tmp_parameters.filename +
                '_CDF_after_Kramers_Kronig_transform')
        if 'thickness' in output:
            thickness = eps._get_navigation_signal(
                data=te[self.axes_manager._get_data_slice(
                    [(axis.index_in_array, 0)])])
            thickness.metadata.General.title = (
                self.metadata.General.title + ' thickness '
                '(calculated using Kramers-Kronig analysis)')
            output['thickness'] = thickness
        if full_output is False:
            return eps
        else:
            return eps, output
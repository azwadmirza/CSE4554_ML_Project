    def get_time_series(self, time_data=True, redshift_data=True,
                        initial_time=None, final_time=None,
                        initial_redshift=None, final_redshift=None,
                        initial_cycle=None, final_cycle=None,
                        times=None, redshifts=None, tolerance=None,
                        parallel=True, setup_function=None):

        """
        Instantiate a DatasetSeries object for a set of outputs.

        If no additional keywords given, a DatasetSeries object will be
        created with all potential datasets created by the simulation.

        Outputs can be gather by specifying a time or redshift range
        (or combination of time and redshift), with a specific list of
        times or redshifts, a range of cycle numbers (for cycle based
        output), or by simply searching all subdirectories within the
        simulation directory.

        time_data : bool
            Whether or not to include time outputs when gathering
            datasets for time series.
            Default: True.
        redshift_data : bool
            Whether or not to include redshift outputs when gathering
            datasets for time series.
            Default: True.
        initial_time : tuple of type (float, str)
            The earliest time for outputs to be included.  This should be
            given as the value and the string representation of the units.
            For example, (5.0, "Gyr").  If None, the initial time of the
            simulation is used.  This can be used in combination with
            either final_time or final_redshift.
            Default: None.
        final_time : tuple of type (float, str)
            The latest time for outputs to be included.  This should be
            given as the value and the string representation of the units.
            For example, (13.7, "Gyr"). If None, the final time of the
            simulation is used.  This can be used in combination with either
            initial_time or initial_redshift.
            Default: None.
        times : tuple of type (float array, str)
            A list of times for which outputs will be found and the units
            of those values.  For example, ([0, 1, 2, 3], "s").
            Default: None.
        initial_redshift : float
            The earliest redshift for outputs to be included.  If None,
            the initial redshift of the simulation is used.  This can be
            used in combination with either final_time or
            final_redshift.
            Default: None.
        final_redshift : float
            The latest redshift for outputs to be included.  If None,
            the final redshift of the simulation is used.  This can be
            used in combination with either initial_time or
            initial_redshift.
            Default: None.
        redshifts : array_like
            A list of redshifts for which outputs will be found.
            Default: None.
        initial_cycle : float
            The earliest cycle for outputs to be included.  If None,
            the initial cycle of the simulation is used.  This can
            only be used with final_cycle.
            Default: None.
        final_cycle : float
            The latest cycle for outputs to be included.  If None,
            the final cycle of the simulation is used.  This can
            only be used in combination with initial_cycle.
            Default: None.
        tolerance : float
            Used in combination with "times" or "redshifts" keywords,
            this is the tolerance within which outputs are accepted
            given the requested times or redshifts.  If None, the
            nearest output is always taken.
            Default: None.
        parallel : bool/int
            If True, the generated DatasetSeries will divide the work
            such that a single processor works on each dataset.  If an
            integer is supplied, the work will be divided into that
            number of jobs.
            Default: True.
        setup_function : callable, accepts a ds
            This function will be called whenever a dataset is loaded.

        Examples
        --------

        >>> import yt
        >>> es = yt.simulation("enzo_tiny_cosmology/32Mpc_32.enzo", "Enzo")
        >>> es.get_time_series(initial_redshift=10, final_time=(13.7, "Gyr"),
                               redshift_data=False)
        >>> for ds in es:
        ...     print(ds.current_time)
        >>> es.get_time_series(redshifts=[3, 2, 1, 0])
        >>> for ds in es:
        ...     print(ds.current_time)

        """

        if (initial_redshift is not None or \
            final_redshift is not None) and \
            not self.cosmological_simulation:
            raise InvalidSimulationTimeSeries(
                "An initial or final redshift has been given for a " +
                "noncosmological simulation.")

        if time_data and redshift_data:
            my_all_outputs = self.all_outputs
        elif time_data:
            my_all_outputs = self.all_time_outputs
        elif redshift_data:
            my_all_outputs = self.all_redshift_outputs
        else:
            raise InvalidSimulationTimeSeries('Both time_data and redshift_data are False.')

        if not my_all_outputs:
            DatasetSeries.__init__(self, outputs=[], parallel=parallel)
            mylog.info("0 outputs loaded into time series.")
            return

        # Apply selection criteria to the set.
        if times is not None:
            my_outputs = self._get_outputs_by_key("time", times,
                                                  tolerance=tolerance,
                                                  outputs=my_all_outputs)

        elif redshifts is not None:
            my_outputs = self._get_outputs_by_key("redshift", redshifts,
                                                  tolerance=tolerance,
                                                  outputs=my_all_outputs)

        elif initial_cycle is not None or final_cycle is not None:
            if initial_cycle is None:
                initial_cycle = 0
            else:
                initial_cycle = max(initial_cycle, 0)
            if final_cycle is None:
                final_cycle = self.parameters['StopCycle']
            else:
                final_cycle = min(final_cycle, self.parameters['StopCycle'])

            my_outputs = my_all_outputs[int(ceil(float(initial_cycle) /
                                                 self.parameters['CycleSkipDataDump'])):
                                        (final_cycle /  self.parameters['CycleSkipDataDump'])+1]

        else:
            if initial_time is not None:
                if isinstance(initial_time, float):
                    my_initial_time = self.quan(initial_time, "code_time")
                elif isinstance(initial_time, tuple) and len(initial_time) == 2:
                    my_initial_time = self.quan(*initial_time)
                elif not isinstance(initial_time, YTArray):
                    raise RuntimeError(
                        "Error: initial_time must be given as a float or " +
                        "tuple of (value, units).")
            elif initial_redshift is not None:
                my_initial_time = self.cosmology.t_from_z(initial_redshift)
            else:
                my_initial_time = self.initial_time

            if final_time is not None:
                if isinstance(final_time, float):
                    my_final_time = self.quan(final_time, "code_time")
                elif isinstance(final_time, tuple) and len(final_time) == 2:
                    my_final_time = self.quan(*final_time)
                elif not isinstance(final_time, YTArray):
                    raise RuntimeError(
                        "Error: final_time must be given as a float or " +
                        "tuple of (value, units).")
            elif final_redshift is not None:
                my_final_time = self.cosmology.t_from_z(final_redshift)
            else:
                my_final_time = self.final_time

            my_initial_time.convert_to_units("s")
            my_final_time.convert_to_units("s")
            my_times = np.array([a['time'] for a in my_all_outputs])
            my_indices = np.digitize([my_initial_time, my_final_time], my_times)
            if my_initial_time == my_times[my_indices[0] - 1]: my_indices[0] -= 1
            my_outputs = my_all_outputs[my_indices[0]:my_indices[1]]

        init_outputs = []
        for output in my_outputs:
            if os.path.exists(output['filename']):
                init_outputs.append(output['filename'])

        DatasetSeries.__init__(self, outputs=init_outputs, parallel=parallel,
                                setup_function=setup_function)
        mylog.info("%d outputs loaded into time series.", len(init_outputs))
    def draw(self, schedule, dt, interp_method, plot_range,
             scaling=None, channels_to_plot=None, plot_all=True,
             table=True, label=False, framechange=True,
             channels=None):
        """Draw figure.

        Args:
            schedule (ScheduleComponent): Schedule to draw
            dt (float): time interval
            interp_method (Callable): interpolation function
                See `qiskit.visualization.interpolation` for more information
            plot_range (tuple[float]): plot range
            scaling (float): Relative visual scaling of waveform amplitudes
            channels_to_plot (list[OutputChannel]): deprecated, see `channels`
            plot_all (bool): if plot all channels even it is empty
            table (bool): Draw event table
            label (bool): Label individual instructions
            framechange (bool): Add framechange indicators
            channels (list[OutputChannel]): channels to draw

        Returns:
            matplotlib.figure: A matplotlib figure object for the pulse schedule
        Raises:
            VisualizationError: when schedule cannot be drawn
        """
        figure = plt.figure()

        if channels_to_plot:
            warnings.warn('The parameter "channels_to_plot" is being replaced by "channels"',
                          DeprecationWarning, 3)
            channels = channels_to_plot

        if not channels:
            channels = []
        interp_method = interp_method or interpolation.step_wise

        # setup plot range
        if plot_range:
            t0 = int(np.floor(plot_range[0]/dt))
            tf = int(np.floor(plot_range[1]/dt))
        else:
            t0 = 0
            # when input schedule is empty or comprises only frame changes,
            # we need to overwrite pulse duration by an integer greater than zero,
            # otherwise waveform returns empty array and matplotlib will be crashed.
            if channels_to_plot:
                tf = schedule.timeslots.ch_duration(*channels_to_plot)
            else:
                tf = schedule.stop_time
            tf = tf or 1

        # prepare waveform channels
        (schedule_channels, output_channels,
         snapshot_channels) = self._build_channels(schedule, channels_to_plot, t0, tf)

        # count numbers of valid waveform
        n_valid_waveform, v_max = self._count_valid_waveforms(output_channels, scaling=scaling,
                                                              channels=channels,
                                                              plot_all=plot_all)

        if table:
            ax = self._draw_table(figure, schedule_channels, dt, n_valid_waveform)

        else:
            ax = figure.add_subplot(111)
            figure.set_size_inches(self.style.figsize[0], self.style.figsize[1])

        ax.set_facecolor(self.style.bg_color)

        y0 = self._draw_channels(ax, output_channels, interp_method,
                                 t0, tf, dt, v_max, label=label,
                                 framechange=framechange)

        self._draw_snapshots(ax, snapshot_channels, dt, y0)

        ax.set_xlim(t0 * dt, tf * dt)
        ax.set_ylim(y0, 1)
        ax.set_yticklabels([])

        return figure
    def _build_channels(self, schedule, channels, t0, tf):
        # prepare waveform channels
        drive_channels = collections.OrderedDict()
        measure_channels = collections.OrderedDict()
        control_channels = collections.OrderedDict()
        acquire_channels = collections.OrderedDict()
        snapshot_channels = collections.OrderedDict()

        _channels = list(schedule.channels) + channels
        _channels = list(set(_channels))

        for chan in _channels:
            if isinstance(chan, DriveChannel):
                try:
                    drive_channels[chan] = EventsOutputChannels(t0, tf)
                except PulseError:
                    pass
            elif isinstance(chan, MeasureChannel):
                try:
                    measure_channels[chan] = EventsOutputChannels(t0, tf)
                except PulseError:
                    pass
            elif isinstance(chan, ControlChannel):
                try:
                    control_channels[chan] = EventsOutputChannels(t0, tf)
                except PulseError:
                    pass
            elif isinstance(chan, AcquireChannel):
                try:
                    acquire_channels[chan] = EventsOutputChannels(t0, tf)
                except PulseError:
                    pass
            elif isinstance(chan, SnapshotChannel):
                try:
                    snapshot_channels[chan] = EventsOutputChannels(t0, tf)
                except PulseError:
                    pass

        output_channels = {**drive_channels, **measure_channels,
                           **control_channels, **acquire_channels}
        channels = {**output_channels, **acquire_channels, **snapshot_channels}
        # sort by index then name to group qubits together.
        output_channels = collections.OrderedDict(sorted(output_channels.items(),
                                                         key=lambda x: (x[0].index, x[0].name)))
        channels = collections.OrderedDict(sorted(channels.items(),
                                                  key=lambda x: (x[0].index, x[0].name)))

        for start_time, instruction in schedule.instructions:
            for channel in instruction.channels:
                if channel in output_channels:
                    output_channels[channel].add_instruction(start_time, instruction)
                elif channel in snapshot_channels:
                    snapshot_channels[channel].add_instruction(start_time, instruction)
        return channels, output_channels, snapshot_channels
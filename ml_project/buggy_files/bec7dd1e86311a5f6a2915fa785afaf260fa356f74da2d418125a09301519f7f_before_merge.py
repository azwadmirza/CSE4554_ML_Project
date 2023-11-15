    def initialise_queue(self):
        if self.queue is None:
            self.queue = get_device().spike_queue(self.source.start, self.source.stop)

        # Update the dt (might have changed between runs)

        self.queue.prepare(self._delays.get_value(), self.source.clock.dt_,
                           self.synapse_sources.get_value())

        if len(set([self.source.clock.dt_,
                    self.synapses.clock.dt_,
                    self.target.clock.dt_])) > 1:
            logger.warn(("Note that the synaptic pathway '{pathway}' will run on the "
                         "clock of the group '{source}' using a dt of {dt}. Either "
                         "the Synapses object '{synapses}' or the target '{target}' "
                         "(or both) are using a different dt. This might lead to "
                         "unexpected results. In particular, all delays will be rounded to "
                         "multiples of {dt}. If in doubt, try to ensure that "
                         "'{source}', '{synapses}', and '{target}' use the "
                         "same dt.").format(pathway=self.name,
                                            source=self.source.name,
                                            target=self.target.name,
                                            dt=self.source.clock.dt,
                                            synapses=self.synapses.name),
                        'synapses_dt_mismatch', once=True)
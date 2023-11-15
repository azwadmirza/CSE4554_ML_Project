    def push(self, sources):
        '''
        Push spikes to the queue.

        Parameters
        ----------
        sources : ndarray of int
            The indices of the neurons that spiked.
        '''
        if len(sources) and len(self._delays):
            start = self._source_start
            stop = self._source_end
            if start > 0:
                start_idx = bisect.bisect_left(sources, start)
            else:
                start_idx = 0
            if stop <= sources[-1]:
                stop_idx = bisect.bisect_left(sources, stop, lo=start_idx)
            else:
                stop_idx = len(self._neurons_to_synapses)
            sources = sources[start_idx:stop_idx]
            if len(sources)==0:
                return
            synapse_indices = self._neurons_to_synapses
            indices = np.concatenate([synapse_indices[source - start]
                                      for source in sources]).astype(np.int32)
            if self._homogeneous:  # homogeneous delays
                self._insert_homogeneous(self._delays[0], indices)
            elif self._offsets is None:  # vectorise over synaptic events
                # there are no precomputed offsets, this is the case
                # (in particular) when there are dynamic delays
                self._insert(self._delays[indices], indices)
            else: # offsets are precomputed
                self._insert(self._delays[indices], indices, self._offsets[indices])
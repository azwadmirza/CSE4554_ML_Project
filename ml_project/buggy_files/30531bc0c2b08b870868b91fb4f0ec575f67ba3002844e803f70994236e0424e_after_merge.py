    def process_squashed_mdblob(self, chunk_data, external_thread=False):
        """
        Process raw concatenated payloads blob. This routine breaks the database access into smaller batches.
        It uses a congestion-control like algorithm to determine the optimal batch size, targeting the
        batch processing time value of self.reference_timedelta.

        :param chunk_data: the blob itself, consists of one or more GigaChannel payloads concatenated together
        :param external_thread: if this is set to True, we add some sleep between batches to allow other threads
        to get the database lock. This is an ugly workaround for Python and Twisted asynchronous programming (locking)
        imperfections. It only makes sense to use it when this routine runs on a non-reactor thread.
        :return ChannelNode objects list if we can correctly load the metadata
        """

        offset = 0
        payload_list = []
        while offset < len(chunk_data):
            payload, offset = read_payload_with_offset(chunk_data, offset)
            payload_list.append(payload)

        result = []
        total_size = len(payload_list)
        start = 0
        while start < total_size:
            end = start + self.batch_size
            batch = payload_list[start:end]
            batch_start_time = datetime.now()

            # We separate the sessions to minimize database locking.
            with db_session:
                for payload in batch:
                    result.extend(self.process_payload(payload))
            if external_thread:
                sleep(self.sleep_on_external_thread)

            # Batch size adjustment
            batch_end_time = datetime.now() - batch_start_time
            target_coeff = (batch_end_time.total_seconds() / self.reference_timedelta.total_seconds())
            if len(batch) == self.batch_size:
                # Adjust batch size only for full batches
                if target_coeff < 0.8:
                    self.batch_size += self.batch_size
                elif target_coeff > 1.0:
                    self.batch_size = int(float(self.batch_size) / target_coeff)
                self.batch_size += 1  # we want to guarantee that at least something will go through
            self._logger.debug(("Added payload batch to DB (entries, seconds): %i %f",
                                (self.batch_size, float(batch_end_time.total_seconds()))))
            start = end
            if self._shutting_down:
                break

        return result
    def _receive(self) -> str:
        if self.source_queue is None:
            raise exceptions.ConfigurationError('pipeline', 'No source queue given.')
        try:
            while True:
                try:
                    retval = self.pipe.lindex(self.internal_queue, -1)  # returns None if no value
                except redis.exceptions.BusyLoadingError:  # Just wait at redis' startup #1334
                    time.sleep(1)
                else:
                    break
            if not retval:
                retval = self.pipe.brpoplpush(self.source_queue,
                                              self.internal_queue, 0)
            return utils.decode(retval)
        except Exception as exc:
            raise exceptions.PipelineError(exc)
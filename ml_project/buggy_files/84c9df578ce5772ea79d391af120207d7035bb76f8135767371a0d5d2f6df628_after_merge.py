    def receive(self):
        try:
            retval = self.pipe.lindex(self.internal_queue, -1)  # returns None if no value
            if not retval:
                retval = self.pipe.brpoplpush(self.source_queue,
                                              self.internal_queue, 0)
            return utils.decode(retval)
        except redis.exceptions.ConnectionError:
            pass  # raised e.g. on SIGHUP
        except Exception as exc:
            raise exceptions.PipelineError(exc)
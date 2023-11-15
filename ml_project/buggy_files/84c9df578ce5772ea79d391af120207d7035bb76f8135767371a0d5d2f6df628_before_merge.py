    def receive(self):
        try:
            if self.pipe.llen(self.internal_queue) > 0:
                return utils.decode(self.pipe.lindex(self.internal_queue, -1))
            return utils.decode(self.pipe.brpoplpush(self.source_queue,
                                                     self.internal_queue, 0))
        except redis.exceptions.ConnectionError:
            pass  # raised e.g. on SIGHUP
        except Exception as exc:
            raise exceptions.PipelineError(exc)
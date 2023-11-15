    def _receive(self) -> bytes:
        if self.source_queue is None:
            raise exceptions.ConfigurationError('pipeline', 'No source queue given.')
        try:
            method, header, body = next(self.channel.consume(self.source_queue))
            if method:
                self.delivery_tag = method.delivery_tag
        except Exception as exc:
            raise exceptions.PipelineError(exc)
        else:
            return body
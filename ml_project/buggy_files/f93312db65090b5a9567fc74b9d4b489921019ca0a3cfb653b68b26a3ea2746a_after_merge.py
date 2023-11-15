    def _receive(self) -> bytes:
        """
        Receives the last not yet acknowledged message.

        Does not block unlike the other pipelines.
        """
        if len(self.state[self.internal_queue]) > 0:
            return utils.decode(self.state[self.internal_queue][0])

        try:
            first_msg = self.state[self.source_queue].pop(0)
        except IndexError as exc:
            raise exceptions.PipelineError(exc)
        self.state[self.internal_queue].append(first_msg)

        return first_msg
    def _receive(self) -> str:
        """
        Receives the last not yet acknowledged message.

        Does not block unlike the other pipelines.
        """
        if len(self.state.get(self.internal_queue, [])) > 0:
            return utils.decode(self.state[self.internal_queue].pop(0))

        first_msg = self.state[self.source_queue].pop(0)

        if self.internal_queue in self.state:
            self.state[self.internal_queue].append(first_msg)
        else:
            self.state[self.internal_queue] = [first_msg]

        return utils.decode(first_msg)
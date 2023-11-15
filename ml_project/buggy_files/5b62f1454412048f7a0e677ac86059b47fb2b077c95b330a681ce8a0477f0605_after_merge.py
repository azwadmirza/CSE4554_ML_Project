    def receive(self) -> str:
        if self._has_message:
            raise exceptions.PipelineError("There's already a message, first "
                                           "acknowledge the existing one.")

        retval = self._receive()
        self._has_message = True
        return utils.decode(retval)
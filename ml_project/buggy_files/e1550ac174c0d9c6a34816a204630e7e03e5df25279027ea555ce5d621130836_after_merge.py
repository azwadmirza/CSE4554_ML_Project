    def _push_pull_grad_async(self, p):
        """Call byteps API to push-pull gradient asynchronously
        Arguments:
            tensor: The tensor to push-pull.
            name: The name of the tensor.
        Returns:
            an push-pull handle and context
        """
        name = self._parameter_names.get(id(p))
        tensor = p.grad
        tensor_compressed, ctx = self._compression.compress(tensor)

        self._locks[p].acquire()
        handle = byteps_push_pull(tensor_compressed, average=True, name="Gradient."+name)
        self._logger.debug("{} calls byteps_push_pull for {}".format(self._desc, self._parameter_names[id(p)]))
        # Add to queue to poll completion
        self._event_queue.put((p, handle, ctx))
        return handle, ctx
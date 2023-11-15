    def _poll(self):
        """Poll the completion of the tensor's backward or push-pull from a FIFO event_queue"""
        while True:
            p, handle, ctx = self._event_queue.get()
            if p is None:
                self._logger.debug("poller exits.")
                break
            # Check whether the push-pull is finished. If so, start updating parameters.
            if handle is not None and poll(handle):
                output = synchronize(handle)
                p.grad.set_(self._compression.decompress(output, ctx))
                self._logger.debug("{} {} finished push-pull".format(self._desc, self._parameter_names[p]))
                self._push_pull_delay[p] = self.backward_passes_per_step
                # So far ByteScheduler only supports SGD, Adam and RMSprop optimizers in torch
                if isinstance(self._opt, torch.optim.SGD):
                    self._sgd(p)
                elif isinstance(self._opt, torch.optim.Adam):
                    self._adam(p)
                elif isinstance(self._opt, torch.optim.RMSprop):
                    self._rmsprop(p)
                else:
                    raise ValueError("Invalid optimizer! ByteScheduler only supports SGD, Adam and RMSprop.")
                self._zero_one_grad(p)
                # notify update completion and parameter is ready for forward propagation
                if p in self._locks:
                    self._locks[p].release()
            else:
                self._event_queue.put((p, handle, ctx))
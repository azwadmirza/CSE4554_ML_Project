    def _hook_var_send_(hook_self):
        def send_(self, workers):
            """
            Sends a Variable object to a (sequence of) Grid workers.

            Args:
            workers: string (or sequence) containing IPFS address(es)
                of worker node(s).
            """

            # makes singleton if needed
            workers = hook_self.local_worker._check_workers(self, workers)
            self = hook_self.local_worker.register_object(hook_self.local_worker,
                                                          obj=self,
                                                          id=self.id,
                                                          owners=workers)
            for worker in workers:
                # TODO: sync or async? likely won't be worth doing async,
                #       but should check (low priority)
                hook_self.local_worker.send_obj(self, worker)

            hook_self.local_worker.register_object(hook_self.local_worker, obj=self, id=self.id,
                                                   owners=self.owners, is_pointer=True)

            return hook_self._var_to_pointer(self, hook_self)

        setattr(torch.autograd.variable.Variable, 'send_', send_)
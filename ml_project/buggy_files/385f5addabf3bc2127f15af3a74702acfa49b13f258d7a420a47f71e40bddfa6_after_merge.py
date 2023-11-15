        def send_(self, workers):
            """
            Sends a Variable object to a (sequence of) Grid workers.

            Args:
            workers: string (or sequence) containing IPFS address(es)
                of worker node(s).
            """

            # makes singleton if needed
            workers = hook_self.local_worker._check_workers(self, workers)

            # NEW OWNERS: this re-registers the current variable to have new owners!
            #  After this line, self.owners should point to workers (the input variable)
            self = hook_self.local_worker.register_object(hook_self.local_worker,
                                                          obj=self,
                                                          id=self.id,
                                                          owners=workers)

            for worker in workers:
                # TODO: sync or async? likely won't be worth doing async,
                #       but should check (low priority)
                hook_self.local_worker.send_obj(self, worker)

            # NEW IS_POINTER STATUS. This line changes the is_pointer flag to true.
            hook_self.local_worker.register_object(hook_self.local_worker, obj=self, id=self.id,
                                                   owners=self.owners, is_pointer=True)

            return hook_self._var_to_pointer(self, hook_self)
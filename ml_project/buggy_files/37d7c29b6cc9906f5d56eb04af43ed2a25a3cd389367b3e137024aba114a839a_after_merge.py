        def get_(self, reduce=lambda x: x[0]):
            """
            Gets a Torch object from its current owners.

            Args:
            reduce: (EXPERIMENTAL) How to reduce tensors that come from
                multiple workers
            """
            # TODO: fully generalize this to multiple workers; consider
            #       adding arguments for other tensor ids, e.g. mapping workers
            #       to tensors, and a reduce function (for example, would allow
            #       for built-in gradient averaging when Variable.get is done)
            #       (low priority)
            try:
                assert len(self.owners) == 1
            except AssertionError:
                raise NotImplementedError('Only able to get_ tensors belonging \
                                            to a single worker right now.')
            if hook_self.local_worker.id in self.owners:
                return self

            _out = hook_self.local_worker.request_obj(obj_id=self.id,
                                                      recipient=self.owners[0])
            x, request_obj_cleanup_method = _out

            hook_self.local_worker.register_object(
                hook_self.local_worker, x, id=x.id)

            # if self == tensor
            _id = hook_self.local_worker.id  # for brevity
            if(type(self) != torch.autograd.variable.Variable and
               type(self) != torch.nn.parameter.Parameter):
                _os = self.old_set_(x.type(self.type()))
                self = hook_self.local_worker.register_object(hook_self.local_worker,
                                                              _os,
                                                              id=self.id, owners=[_id])

            else:

                _os = self.old_set_(x.type(self.data.type()))  # for brevity
                self = hook_self.local_worker.register_object(hook_self.local_worker,
                                                              _os,
                                                              id=self.id, owners=[_id])

                self.data = hook_self.local_worker.register_object(hook_self.local_worker,
                                                                   x.data,
                                                                   id=x.data.id,
                                                                   owners=[_id])
                if(x.grad is not None):
                    self.grad = hook_self.local_worker.register_object(hook_self.local_worker,
                                                                       x.grad,
                                                                       id=x.grad.id,
                                                                       owners=[_id])

            """for some reason, when retuning obj from request_obj
            method (above), the gradient gets re-initialized without
            being re-registered and as a consequence does not have an
            id, causing the last register_object above to fail
            because x.grad.id does not exist. As a result, we've needed
            to register objects temporarily which seems to
            fix it. Super strange bug which took multiple days to figure
            out. The true cause is still unknown but this
            workaround seems to work well for now. Anyway, we don't need
            the temporary objects past this point.
            request_obj_cleanup_method()"""
            return self
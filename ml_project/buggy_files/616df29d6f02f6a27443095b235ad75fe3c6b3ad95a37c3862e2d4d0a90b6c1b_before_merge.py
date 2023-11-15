    def _hook_new_grad(hook_self):

        @property
        def new_grad(self):
            if not hasattr(self, 'grad_registered'):

                if self.old_grad is not None:

                    if(hasattr(self.old_grad, 'id')):
                        grad_id = self.old_grad.id
                    else:
                        grad_id = None

                    if(not hasattr(self, 'owners')):
                        hook_self.local_worker.register_object(hook_self.local_worker,
                                                               obj=self,
                                                               owners=[
                                                                   hook_self.local_worker.id],
                                                               is_pointer=False)

                    _ip = self.is_pointer
                    self.old_grad = hook_self.local_worker.register_object(hook_self.local_worker,
                                                                           obj=self.old_grad,
                                                                           owners=self.owners,
                                                                           id=grad_id,
                                                                           is_pointer=_ip)
                    self.grad_registered = True

            return self.old_grad

        @new_grad.setter
        def new_grad(self, new):
            self.old_grad = new

        torch.autograd.variable.Variable.grad = new_grad
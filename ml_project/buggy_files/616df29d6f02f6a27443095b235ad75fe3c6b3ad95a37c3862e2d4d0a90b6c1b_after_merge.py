    def _hook_new_grad(hook_self):

        @property
        def new_grad(self):
            if not hasattr(self, 'grad_registered'):

                if self.old_grad is not None:

                    if(hasattr(self.old_grad, 'id')):
                        grad_id = self.old_grad.id
                    else:
                        grad_id = None

                    # this seems a little sketch - why are we having to check to see whether
                    # the parent has been registered. Is there and edge case where gradients
                    # are created before their parents? TODO: fix
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

                    # DO NOT REMOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING
                    # for context behidn this edit you can see the following video
                    # https://www.twitch.tv/videos/275838386
                    # long story short, we need to actually run the grad generating
                    # function (self.old_grad) and cache its value (the variable's
                    # gradient) in self.grad_backup so that python garbage collection
                    # doesn't delete the python object as a part of PyTorch's C++
                    # wrapping craziness (which does a lot of re-instantiating objects)
                    # In this case, re-instantiating the object gives it a new id because
                    # the object containing the old id goes away... this id is random which
                    # can create problems for PySyft

                    # also - keep this running ONLY within the if statement above that checks
                    # to see if self.grad_registered is not yet an attribute
                    self.grad_backup = self.old_grad
                    self.grad_backup.owners_backup = self.grad_backup.owners

            return self.old_grad

        @new_grad.setter
        def new_grad(self, new):
            self.old_grad = new

        torch.autograd.variable.Variable.grad = new_grad
    def register_object(self, worker, obj, force_attach_to_worker=False,
                        temporary=False, **kwargs):
        """
        Registers an object with the current worker node. Selects an
        id for the object, assigns a list of owners,
        and establishes whether it's a pointer or not. This method
        is generally not used by the client and is
        instead used by interal processes (hooks and workers).

        :Parameters:

        * **obj (a torch.Tensor or torch.autograd.Variable)** a Torch
          instance, e.g. Tensor or Variable to be registered

        * **force_attach_to_worker (bool)** if set to True, it will
          force the object to be stored in the worker's permanent registry

        * **temporary (bool)** If set to True, it will store the object
          in the worker's temporary registry.

        :kwargs:

        * **id (int or string)** random integer between 0 and 1e10 or
          string uniquely identifying the object.

        * **owners (list of ** :class:`BaseWorker` objects ** or ids)**
          owner(s) of the object

        * **is_pointer (bool, optional)** Whether or not the tensor being
          registered contains the data locally or is instead a pointer to
          a tensor that lives on a different worker.
        """
        # TODO: Assign default id more intelligently (low priority)
        #       Consider popping id from long list of unique integers

        keys = kwargs.keys()

        # DO NOT DELETE THIS TRY/CATCH UNLESS YOU KNOW WHAT YOU'RE DOING
        # PyTorch tensors wrapped invariables (if my_var.data) are python
        # objects that get deleted and re-created randomly according to
        # the whims of the PyTorch wizards. Thus, our attributes were getting
        # deleted with them (because they are not present in the underlying
        # C++ code.) Thus, so that these python objects do NOT get garbage
        # collected, we're creating a secondary reference to them from the
        # parent Variable object (which we have been told is stable). This
        # is experimental functionality but seems to solve the symptoms we
        # were previously experiencing.
        try:
            obj.data_backup = obj.data
        except:
            ""

        obj.id = (kwargs['id']
                  if ('id' in keys and kwargs['id'] is not None)
                  else random.randint(0, 1e10))

        obj.owners = (kwargs['owners']
                      if 'owners' in keys
                      else [worker.id])

        # check to see if we can resolve owner id to pointer
        owner_pointers = list()
        for owner in obj.owners:
            if owner in self._known_workers.keys():
                owner_pointers.append(self._known_workers[owner])
            else:
                owner_pointers.append(owner)
        obj.owners = owner_pointers

        obj.is_pointer = (kwargs['is_pointer']
                          if 'is_pointer' in keys
                          else False)

        mal_points_away = obj.is_pointer and worker.id in obj.owners
        # print("Mal Points Away:" + str(mal_points_away))
        # print("self.local_worker.id in obj.owners == " + str(self.local_worker.id in obj.owners))
        # The following was meant to assure that we didn't try to
        # register objects we didn't have. We end up needing to register
        # objects with non-local owners on the worker side before sending
        # things off, so it's been relaxed.  Consider using a 'strict'
        # kwarg for strict checking of this stuff
        mal_points_here = False
        # mal_points_here = not obj.is_pointer and self.local_worker.id not in obj.owners
        if mal_points_away or mal_points_here:
            raise RuntimeError(
                'Invalid registry: is_pointer is {} but owners is {} on tensor {}'.format(
                    obj.is_pointer, obj.owners, obj.id))
        # print("setting object:" + str(obj.id))
        self.set_obj(obj.id, obj, force=force_attach_to_worker, tmp=temporary)

        # Perform recursive operations.
        # If there is a child tensor (self.data)
        if(hasattr(obj, 'grad')):
            if(obj.grad is not None):
                self.register_object(worker=worker,
                                     obj=obj.grad,
                                     force_attach_to_worker=force_attach_to_worker,
                                     temporary=temporary,
                                     id=obj.grad.id,
                                     owners=obj.owners,
                                     is_pointer=obj.is_pointer)
        try:
            _ = obj.data
            _ = str(_)  # just a style issue
            if(obj.data is not None):
                self.register_object(worker=worker,
                                     obj=obj.data,
                                     force_attach_to_worker=force_attach_to_worker,
                                     temporary=temporary,
                                     id=obj.data.id,
                                     owners=obj.owners,
                                     is_pointer=obj.is_pointer)

        except RuntimeError:
            ""

        return obj
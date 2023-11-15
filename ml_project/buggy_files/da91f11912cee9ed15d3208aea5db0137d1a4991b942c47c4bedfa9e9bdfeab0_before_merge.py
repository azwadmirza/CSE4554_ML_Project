    def create_pointer(
        tensor,
        location: Union[AbstractWorker, str] = None,
        id_at_location: (str or int) = None,
        register: bool = False,
        owner: Union[AbstractWorker, str] = None,
        ptr_id: (str or int) = None,
        garbage_collect_data=None,
        shape=None,
    ) -> "PointerTensor":
        """Creates a pointer to the "self" FrameworkTensor object.

        This method is called on a FrameworkTensor object, returning a pointer
        to that object. This method is the CORRECT way to create a pointer,
        and the parameters of this method give all possible attributes that
        a pointer can be created with.

        Args:
            location: The AbstractWorker object which points to the worker on which
                this pointer's object can be found. In nearly all cases, this
                is self.owner and so this attribute can usually be left blank.
                Very rarely you may know that you are about to move the Tensor
                to another worker so you can pre-initialize the location
                attribute of the pointer to some other worker, but this is a
                rare exception.
            id_at_location: A string or integer id of the tensor being pointed
                to. Similar to location, this parameter is almost always
                self.id and so you can leave this parameter to None. The only
                exception is if you happen to know that the ID is going to be
                something different than self.id, but again this is very rare
                and most of the time, setting this means that you are probably
                doing something you shouldn't.
            register: A boolean parameter (default False) that determines
                whether to register the new pointer that gets created. This is
                set to false by default because most of the time a pointer is
                initialized in this way so that it can be sent to someone else
                (i.e., "Oh you need to point to my tensor? let me create a
                pointer and send it to you" ). Thus, when a pointer gets
                created, we want to skip being registered on the local worker
                because the pointer is about to be sent elsewhere. However, if
                you are initializing a pointer you intend to keep, then it is
                probably a good idea to register it, especially if there is any
                chance that someone else will initialize a pointer to your
                pointer.
            owner: A AbstractWorker parameter to specify the worker on which the
                pointer is located. It is also where the pointer is registered
                if register is set to True.
            ptr_id: A string or integer parameter to specify the id of the pointer
                in case you wish to set it manually for any special reason.
                Otherwise, it will be set randomly.
            garbage_collect_data: If true (default), delete the remote tensor when the
                pointer is deleted.

        Returns:
            A FrameworkTensor[PointerTensor] pointer to self. Note that this
            object itself will likely be wrapped by a FrameworkTensor wrapper.
        """
        if owner is None:
            owner = tensor.owner

        if location is None:
            location = tensor.owner

        owner = tensor.owner.get_worker(owner)
        location = tensor.owner.get_worker(location)

        # previous_pointer = owner.get_pointer_to(location, id_at_location)
        previous_pointer = None

        if previous_pointer is None:
            ptr = PointerTensor(
                location=location,
                id_at_location=id_at_location,
                owner=owner,
                id=ptr_id,
                garbage_collect_data=True if garbage_collect_data is None else garbage_collect_data,
                shape=shape,
                tags=tensor.tags,
                description=tensor.description,
            )

        return ptr
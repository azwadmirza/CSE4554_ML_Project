    def _get_hooked_method(cls, tensor_type, method_name):
        """
        Hook a method in order to replace all args/kwargs syft/torch tensors with
        their child attribute if they exist
        If so, forward this method with the new args and new self, get response
        and "rebuild" the torch tensor wrapper upon all tensors found
        If not, just execute the native torch methodn

        Args:
            attr (str): the method to hook
        Return:
            the hooked method
        """

        @wraps(getattr(tensor_type, method_name))
        def overloaded_native_method(self, *args, **kwargs):
            """
            Operate the hooking
            """

            if not hasattr(self, "child"):  # means that it's not a wrapper

                # if self is a natural tensor but the first argument isn't,
                # wrap self with the appropriate type and re-run
                if len(args) > 0 and hasattr(args[0], "child"):

                    # if we allow this for PointerTensors it opens the potential
                    # that we could accidentally serialize and send a tensor in the
                    # arguments
                    if not isinstance(args[0].child, PointerTensor):
                        self = type(args[0].child)().on(self, wrap=True)
                        args = [args[0]]
                        return overloaded_native_method(self, *args, **kwargs)

                method = getattr(self, f"native_{method_name}")
                # Run the native function with the new args

                try:
                    response = method(*args, **kwargs)

                except BaseException as e:
                    # we can make some errors more descriptive with this method
                    raise route_method_exception(e, self, args, kwargs)

            else:  # means that there is a wrapper to remove

                try:
                    # Replace all torch tensor with their child attribute
                    new_self, new_args, new_kwargs = hook_args.unwrap_args_from_method(
                        method_name, self, args, kwargs
                    )

                except BaseException as e:  # if there's a type mismatch, try to fix it!

                    try:
                        # if the first argument has no child (meaning it's probably raw data),
                        # try wrapping it with the type of self. We have to except PointerTensor
                        # because otherwise it can lead to inadvertently sending data to another
                        # machine
                        if not hasattr(args[0], "child") and not isinstance(
                            self.child, PointerTensor
                        ):
                            # TODO: add check to make sure this isn't getting around a security class

                            _args = list()
                            _args.append(type(self)().on(args[0], wrap=False))
                            for a in args[1:]:
                                _args.append(a)

                            args = _args

                        # Replace all torch tensor with their child attribute
                        new_self, new_args, new_kwargs = hook_args.unwrap_args_from_method(
                            method_name, self, args, kwargs
                        )
                    except BaseException as e:
                        # we can make some errors more descriptive with this method
                        raise route_method_exception(e, self, args, kwargs)

                # Send the new command to the appropriate class and get the response
                method = getattr(new_self, method_name)
                response = method(*new_args, **new_kwargs)

                # For inplace methods, just directly return self
                if syft.framework.is_inplace_method(method_name):
                    return self

                # Put back the wrappers where needed
                response = hook_args.hook_response(
                    method_name,
                    response,
                    wrap_type=type(self),
                    new_self=self,
                    wrap_args=self.get_class_attributes(),
                )

            return response

        return overloaded_native_method
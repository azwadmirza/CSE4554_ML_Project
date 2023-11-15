def actor_handle_from_class(Class, class_id, resources, checkpoint_interval):
    class_name = Class.__name__.encode("ascii")
    actor_handle_class = make_actor_handle_class(class_name)
    exported = []

    class ActorHandle(actor_handle_class):

        @classmethod
        def remote(cls, *args, **kwargs):
            if ray.worker.global_worker.mode is None:
                raise Exception("Actors cannot be created before ray.init() "
                                "has been called.")

            actor_id = random_actor_id()
            # The ID for this instance of ActorHandle. These should be unique
            # across instances with the same _ray_actor_id.
            actor_handle_id = ray.local_scheduler.ObjectID(
                ray.worker.NIL_ACTOR_ID)
            # The actor cursor is a dummy object representing the most recent
            # actor method invocation. For each subsequent method invocation,
            # the current cursor should be added as a dependency, and then
            # updated to reflect the new invocation.
            actor_cursor = None
            # The number of actor method invocations that we've called so far.
            actor_counter = 0
            # Get the actor methods of the given class.
            actor_methods = inspect.getmembers(
                Class, predicate=(lambda x: (inspect.isfunction(x) or
                                             inspect.ismethod(x) or
                                             is_cython(x))))
            # Extract the signatures of each of the methods. This will be used
            # to catch some errors if the methods are called with inappropriate
            # arguments.
            method_signatures = dict()
            for k, v in actor_methods:
                # Print a warning message if the method signature is not
                # supported. We don't raise an exception because if the actor
                # inherits from a class that has a method whose signature we
                # don't support, we there may not be much the user can do about
                # it.
                signature.check_signature_supported(v, warn=True)
                method_signatures[k] = signature.extract_signature(
                    v, ignore_first=True)

            actor_method_names = [method_name for method_name, _ in
                                  actor_methods]
            actor_method_num_return_vals = []
            for _, method in actor_methods:
                if hasattr(method, "__ray_num_return_vals__"):
                    actor_method_num_return_vals.append(
                        method.__ray_num_return_vals__)
                else:
                    actor_method_num_return_vals.append(1)
            # Do not export the actor class or the actor if run in PYTHON_MODE
            # Instead, instantiate the actor locally and add it to
            # global_worker's dictionary
            if ray.worker.global_worker.mode == ray.PYTHON_MODE:
                ray.worker.global_worker.actors[actor_id] = (
                    Class.__new__(Class))
            else:
                # Export the actor.
                if not exported:
                    export_actor_class(class_id, Class, actor_method_names,
                                       actor_method_num_return_vals,
                                       checkpoint_interval,
                                       ray.worker.global_worker)
                    exported.append(0)
                export_actor(actor_id, class_id, class_name,
                             actor_method_names, actor_method_num_return_vals,
                             resources, ray.worker.global_worker)

            # Instantiate the actor handle.
            actor_object = cls.__new__(cls)
            actor_object._manual_init(actor_id, actor_handle_id, actor_cursor,
                                      actor_counter, actor_method_names,
                                      actor_method_num_return_vals,
                                      method_signatures,
                                      checkpoint_interval)

            # Call __init__ as a remote function.
            if "__init__" in actor_object._ray_actor_method_names:
                actor_object._actor_method_call("__init__", args=args,
                                                kwargs=kwargs)
            else:
                print("WARNING: this object has no __init__ method.")

            return actor_object

    return ActorHandle
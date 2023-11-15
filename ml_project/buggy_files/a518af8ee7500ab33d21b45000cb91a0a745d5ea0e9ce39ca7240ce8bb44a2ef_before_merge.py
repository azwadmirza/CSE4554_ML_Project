def make_actor(cls, resources, checkpoint_interval):
    # Print warning if this actor requires custom resources.
    for resource_name in resources:
        if resource_name not in ["CPU", "GPU"]:
            raise Exception("Currently only GPU resources can be used for "
                            "actor placement.")
    if checkpoint_interval == 0:
        raise Exception("checkpoint_interval must be greater than 0.")

    # Modify the class to have an additional method that will be used for
    # terminating the worker.
    class Class(cls):
        def __ray_terminate__(self, actor_id):
            # Record that this actor has been removed so that if this node
            # dies later, the actor won't be recreated. Alternatively, we could
            # remove the actor key from Redis here.
            ray.worker.global_worker.redis_client.hset(b"Actor:" + actor_id,
                                                       "removed", True)
            # Release the GPUs that this worker was using.
            if len(ray.get_gpu_ids()) > 0:
                release_gpus_in_use(
                    ray.worker.global_worker.driver_id,
                    ray.worker.global_worker.local_scheduler_id,
                    ray.get_gpu_ids(),
                    ray.worker.global_worker.redis_client)
            # Disconnect the worker from the local scheduler. The point of this
            # is so that when the worker kills itself below, the local
            # scheduler won't push an error message to the driver.
            ray.worker.global_worker.local_scheduler_client.disconnect()
            import os
            os._exit(0)

        def __ray_save_checkpoint__(self):
            if hasattr(self, "__ray_save__"):
                object_to_serialize = self.__ray_save__()
            else:
                object_to_serialize = self
            return pickle.dumps(object_to_serialize)

        @classmethod
        def __ray_restore_from_checkpoint__(cls, pickled_checkpoint):
            checkpoint = pickle.loads(pickled_checkpoint)
            if hasattr(cls, "__ray_restore__"):
                actor_object = cls.__new__(cls)
                actor_object.__ray_restore__(checkpoint)
            else:
                # TODO(rkn): It's possible that this will cause problems. When
                # you unpickle the same object twice, the two objects will not
                # have the same class.
                actor_object = checkpoint
            return actor_object

        def __ray_checkpoint__(self):
            """Save a checkpoint.

            This task saves the current state of the actor, the current task
            frontier according to the local scheduler, and the checkpoint index
            (number of tasks executed so far).
            """
            worker = ray.worker.global_worker
            checkpoint_index = worker.actor_task_counter
            # Get the state to save.
            checkpoint = self.__ray_save_checkpoint__()
            # Get the current task frontier, per actor handle.
            # NOTE(swang): This only includes actor handles that the local
            # scheduler has seen. Handle IDs for which no task has yet reached
            # the local scheduler will not be included, and may not be runnable
            # on checkpoint resumption.
            actor_id = ray.local_scheduler.ObjectID(worker.actor_id)
            frontier = worker.local_scheduler_client.get_actor_frontier(
                actor_id)
            # Save the checkpoint in Redis. TODO(rkn): Checkpoints
            # should not be stored in Redis. Fix this.
            set_actor_checkpoint(worker, worker.actor_id, checkpoint_index,
                                 checkpoint, frontier)

        def __ray_checkpoint_restore__(self):
            """Restore a checkpoint.

            This task looks for a saved checkpoint and if found, restores the
            state of the actor, the task frontier in the local scheduler, and
            the checkpoint index (number of tasks executed so far).

            Returns:
                A bool indicating whether a checkpoint was resumed.
            """
            worker = ray.worker.global_worker
            # Get the most recent checkpoint stored, if any.
            checkpoint_index, checkpoint, frontier = get_actor_checkpoint(
                worker, worker.actor_id)
            # Try to resume from the checkpoint.
            checkpoint_resumed = False
            if checkpoint_index is not None:
                # Load the actor state from the checkpoint.
                worker.actors[worker.actor_id] = (
                    worker.actor_class.__ray_restore_from_checkpoint__(
                        checkpoint))
                # Set the number of tasks executed so far.
                worker.actor_task_counter = checkpoint_index
                # Set the actor frontier in the local scheduler.
                worker.local_scheduler_client.set_actor_frontier(frontier)
                checkpoint_resumed = True

            return checkpoint_resumed

    Class.__module__ = cls.__module__
    Class.__name__ = cls.__name__

    class_id = random_actor_class_id()

    return actor_handle_from_class(Class, class_id, resources,
                                   checkpoint_interval)
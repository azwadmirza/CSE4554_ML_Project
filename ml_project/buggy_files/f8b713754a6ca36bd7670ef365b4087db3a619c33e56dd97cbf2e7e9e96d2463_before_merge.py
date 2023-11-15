    def done_callback(future):
        result = future.result()
        # Result from async plasma, transparently pass it to user future
        if isinstance(future, PlasmaObjectFuture):
            if isinstance(result, ray.exceptions.RayTaskError):
                ray.worker.last_task_error_raise_time = time.time()
                user_future.set_exception(result.as_instanceof_cause())
            else:
                user_future.set_result(result)
        else:
            # Result from direct call.
            assert isinstance(result, AsyncGetResponse), result
            if result.plasma_fallback_id is None:
                if isinstance(result.result, ray.exceptions.RayTaskError):
                    ray.worker.last_task_error_raise_time = time.time()
                    user_future.set_exception(
                        result.result.as_instanceof_cause())
                else:
                    user_future.set_result(result.result)
            else:
                # Schedule plasma to async get, use the the same callback.
                retry_plasma_future = as_future(result.plasma_fallback_id)
                retry_plasma_future.add_done_callback(done_callback)
                # A hack to keep reference to the future so it doesn't get GC.
                user_future.retry_plasma_future = retry_plasma_future
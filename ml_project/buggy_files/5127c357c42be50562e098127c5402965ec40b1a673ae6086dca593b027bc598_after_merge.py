    def stop(self):
        try:
            destroy_futures = []
            for actor in (self._cpu_calc_actors + self._sender_actors + self._inproc_holder_actors
                          + self._inproc_io_runner_actors + self._cuda_calc_actors
                          + self._cuda_holder_actors + self._receiver_actors + self._spill_actors
                          + self._process_helper_actors):
                if actor and actor.ctx:
                    destroy_futures.append(actor.destroy(wait=False))

            if self._result_sender_ref:
                destroy_futures.append(self._result_sender_ref.destroy(wait=False))
            if self._status_ref:
                destroy_futures.append(self._status_ref.destroy(wait=False))
            if self._shared_holder_ref:
                destroy_futures.append(self._shared_holder_ref.destroy(wait=False))
            if self._storage_manager_ref:
                destroy_futures.append(self._storage_manager_ref.destroy(wait=False))
            if self._events_ref:
                destroy_futures.append(self._events_ref.destroy(wait=False))
            if self._dispatch_ref:
                destroy_futures.append(self._dispatch_ref.destroy(wait=False))
            if self._execution_ref:
                destroy_futures.append(self._execution_ref.destroy(wait=False))
            [f.result(5) for f in destroy_futures]
        finally:
            self._plasma_store.__exit__(None, None, None)
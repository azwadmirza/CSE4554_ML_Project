    def stop(self):
        try:
            for actor in (self._cpu_calc_actors + self._sender_actors + self._inproc_holder_actors
                          + self._inproc_io_runner_actors + self._cuda_calc_actors
                          + self._cuda_holder_actors + self._receiver_actors + self._spill_actors
                          + self._process_helper_actors):
                if actor and actor.ctx:
                    actor.destroy(wait=False)

            if self._result_sender_ref:
                self._result_sender_ref.destroy(wait=False)
            if self._status_ref:
                self._status_ref.destroy(wait=False)
            if self._shared_holder_ref:
                self._shared_holder_ref.destroy(wait=False)
            if self._storage_manager_ref:
                self._storage_manager_ref.destroy(wait=False)
            if self._events_ref:
                self._events_ref.destroy(wait=False)
            if self._dispatch_ref:
                self._dispatch_ref.destroy(wait=False)
            if self._execution_ref:
                self._execution_ref.destroy(wait=False)
        finally:
            self._plasma_store.__exit__(None, None, None)
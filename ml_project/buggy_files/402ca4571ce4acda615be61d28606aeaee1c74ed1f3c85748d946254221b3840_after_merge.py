    def retrieve_and_deserialize(self, object_ids, timeout, error_timeout=10):
        start_time = time.time()
        # Only send the warning once.
        warning_sent = False
        while True:
            try:
                # We divide very large get requests into smaller get requests
                # so that a single get request doesn't block the store for a
                # long time, if the store is blocked, it can block the manager
                # as well as a consequence.
                results = []
                for i in range(0, len(object_ids),
                               ray._config.worker_get_request_size()):
                    results += self.plasma_client.get(
                        object_ids[i:(i +
                                      ray._config.worker_get_request_size())],
                        timeout,
                        self.serialization_context)
                return results
            except pyarrow.lib.ArrowInvalid as e:
                # TODO(ekl): the local scheduler could include relevant
                # metadata in the task kill case for a better error message
                invalid_error = RayTaskError(
                    "<unknown>", None,
                    "Invalid return value: likely worker died or was killed "
                    "while executing the task.")
                return [invalid_error] * len(object_ids)
            except pyarrow.DeserializationCallbackError as e:
                # Wait a little bit for the import thread to import the class.
                # If we currently have the worker lock, we need to release it
                # so that the import thread can acquire it.
                if self.mode == WORKER_MODE:
                    self.lock.release()
                time.sleep(0.01)
                if self.mode == WORKER_MODE:
                    self.lock.acquire()

                if time.time() - start_time > error_timeout:
                    warning_message = ("This worker or driver is waiting to "
                                       "receive a class definition so that it "
                                       "can deserialize an object from the "
                                       "object store. This may be fine, or it "
                                       "may be a bug.")
                    if not warning_sent:
                        self.push_error_to_driver(self.task_driver_id.id(),
                                                  "wait_for_class",
                                                  warning_message)
                    warning_sent = True
def import_thread(worker, mode):
    worker.import_pubsub_client = worker.redis_client.pubsub()
    # Exports that are published after the call to
    # import_pubsub_client.subscribe and before the call to
    # import_pubsub_client.listen will still be processed in the loop.
    worker.import_pubsub_client.subscribe("__keyspace@0__:Exports")
    # Keep track of the number of imports that we've imported.
    num_imported = 0

    # Get the exports that occurred before the call to subscribe.
    with worker.lock:
        export_keys = worker.redis_client.lrange("Exports", 0, -1)
        for key in export_keys:
            num_imported += 1

            # Handle the driver case first.
            if mode != WORKER_MODE:
                if key.startswith(b"FunctionsToRun"):
                    fetch_and_execute_function_to_run(key, worker=worker)
                # Continue because FunctionsToRun are the only things that the
                # driver should import.
                continue

            if key.startswith(b"RemoteFunction"):
                fetch_and_register_remote_function(key, worker=worker)
            elif key.startswith(b"FunctionsToRun"):
                fetch_and_execute_function_to_run(key, worker=worker)
            elif key.startswith(b"ActorClass"):
                # If this worker is an actor that is supposed to construct this
                # class, fetch the actor and class information and construct
                # the class.
                class_id = key.split(b":", 1)[1]
                if (worker.actor_id != NIL_ACTOR_ID and
                        worker.class_id == class_id):
                    worker.fetch_and_register_actor(key, worker)
            else:
                raise Exception("This code should be unreachable.")

    try:
        for msg in worker.import_pubsub_client.listen():
            with worker.lock:
                if msg["type"] == "subscribe":
                    continue
                assert msg["data"] == b"rpush"
                num_imports = worker.redis_client.llen("Exports")
                assert num_imports >= num_imported
                for i in range(num_imported, num_imports):
                    num_imported += 1
                    key = worker.redis_client.lindex("Exports", i)

                    # Handle the driver case first.
                    if mode != WORKER_MODE:
                        if key.startswith(b"FunctionsToRun"):
                            with log_span("ray:import_function_to_run",
                                          worker=worker):
                                fetch_and_execute_function_to_run(
                                    key, worker=worker)
                        # Continue because FunctionsToRun are the only things
                        # that the driver should import.
                        continue

                    if key.startswith(b"RemoteFunction"):
                        with log_span("ray:import_remote_function",
                                      worker=worker):
                            fetch_and_register_remote_function(key,
                                                               worker=worker)
                    elif key.startswith(b"FunctionsToRun"):
                        with log_span("ray:import_function_to_run",
                                      worker=worker):
                            fetch_and_execute_function_to_run(key,
                                                              worker=worker)
                    elif key.startswith(b"Actor"):
                        # Only get the actor if the actor ID matches the actor
                        # ID of this worker.
                        actor_id, = worker.redis_client.hmget(key, "actor_id")
                        if worker.actor_id == actor_id:
                            worker.fetch_and_register["Actor"](key, worker)
                    else:
                        raise Exception("This code should be unreachable.")
    except redis.ConnectionError:
        # When Redis terminates the listen call will throw a ConnectionError,
        # which we catch here.
        pass
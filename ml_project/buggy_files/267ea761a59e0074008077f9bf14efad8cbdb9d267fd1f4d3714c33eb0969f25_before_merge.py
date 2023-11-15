def connect(info, object_id_seed=None, mode=WORKER_MODE, worker=global_worker,
            actor_id=NIL_ACTOR_ID):
    """Connect this worker to the local scheduler, to Plasma, and to Redis.

    Args:
        info (dict): A dictionary with address of the Redis server and the
            sockets of the plasma store, plasma manager, and local scheduler.
        object_id_seed: A seed to use to make the generation of object IDs
            deterministic.
        mode: The mode of the worker. One of SCRIPT_MODE, WORKER_MODE,
            PYTHON_MODE, and SILENT_MODE.
        actor_id: The ID of the actor running on this worker. If this worker is
            not an actor, then this is NIL_ACTOR_ID.
    """
    check_main_thread()
    # Do some basic checking to make sure we didn't call ray.init twice.
    error_message = "Perhaps you called ray.init twice by accident?"
    assert not worker.connected, error_message
    assert worker.cached_functions_to_run is not None, error_message
    assert worker.cached_remote_functions_and_actors is not None, error_message
    # Initialize some fields.
    worker.worker_id = random_string()
    worker.actor_id = actor_id
    worker.connected = True
    worker.set_mode(mode)
    # The worker.events field is used to aggregate logging information and
    # display it in the web UI. Note that Python lists protected by the GIL,
    # which is important because we will append to this field from multiple
    # threads.
    worker.events = []
    # If running Ray in PYTHON_MODE, there is no need to create call
    # create_worker or to start the worker service.
    if mode == PYTHON_MODE:
        return
    # Set the node IP address.
    worker.node_ip_address = info["node_ip_address"]
    worker.redis_address = info["redis_address"]

    # Create a Redis client.
    redis_ip_address, redis_port = info["redis_address"].split(":")
    worker.redis_client = redis.StrictRedis(host=redis_ip_address,
                                            port=int(redis_port))

    # For driver's check that the version information matches the version
    # information that the Ray cluster was started with.
    try:
        ray.services.check_version_info(worker.redis_client)
    except Exception as e:
        if mode in [SCRIPT_MODE, SILENT_MODE]:
            raise e
        elif mode == WORKER_MODE:
            traceback_str = traceback.format_exc()
            ray.utils.push_error_to_driver(worker.redis_client,
                                           "version_mismatch",
                                           traceback_str,
                                           driver_id=None)

    worker.lock = threading.Lock()

    # Check the RedirectOutput key in Redis and based on its value redirect
    # worker output and error to their own files.
    if mode == WORKER_MODE:
        # This key is set in services.py when Redis is started.
        redirect_worker_output_val = worker.redis_client.get("RedirectOutput")
        if (redirect_worker_output_val is not None and
                int(redirect_worker_output_val) == 1):
            redirect_worker_output = 1
        else:
            redirect_worker_output = 0
        if redirect_worker_output:
            log_stdout_file, log_stderr_file = services.new_log_files("worker",
                                                                      True)
            sys.stdout = log_stdout_file
            sys.stderr = log_stderr_file
            services.record_log_files_in_redis(info["redis_address"],
                                               info["node_ip_address"],
                                               [log_stdout_file,
                                                log_stderr_file])

    # Create an object for interfacing with the global state.
    global_state._initialize_global_state(redis_ip_address, int(redis_port))

    # Register the worker with Redis.
    if mode in [SCRIPT_MODE, SILENT_MODE]:
        # The concept of a driver is the same as the concept of a "job".
        # Register the driver/job with Redis here.
        import __main__ as main
        driver_info = {
            "node_ip_address": worker.node_ip_address,
            "driver_id": worker.worker_id,
            "start_time": time.time(),
            "plasma_store_socket": info["store_socket_name"],
            "plasma_manager_socket": info["manager_socket_name"],
            "local_scheduler_socket": info["local_scheduler_socket_name"]}
        driver_info["name"] = (main.__file__ if hasattr(main, "__file__")
                               else "INTERACTIVE MODE")
        worker.redis_client.hmset(b"Drivers:" + worker.worker_id, driver_info)
        if not worker.redis_client.exists("webui"):
            worker.redis_client.hmset("webui", {"url": info["webui_url"]})
        is_worker = False
    elif mode == WORKER_MODE:
        # Register the worker with Redis.
        worker_dict = {
            "node_ip_address": worker.node_ip_address,
            "plasma_store_socket": info["store_socket_name"],
            "plasma_manager_socket": info["manager_socket_name"],
            "local_scheduler_socket": info["local_scheduler_socket_name"]}
        if redirect_worker_output:
            worker_dict["stdout_file"] = os.path.abspath(log_stdout_file.name)
            worker_dict["stderr_file"] = os.path.abspath(log_stderr_file.name)
        worker.redis_client.hmset(b"Workers:" + worker.worker_id, worker_dict)
        is_worker = True
    else:
        raise Exception("This code should be unreachable.")

    # Create an object store client.
    worker.plasma_client = plasma.connect(info["store_socket_name"],
                                          info["manager_socket_name"],
                                          64)
    # Create the local scheduler client.
    if worker.actor_id != NIL_ACTOR_ID:
        num_gpus = int(worker.redis_client.hget(b"Actor:" + actor_id,
                                                "num_gpus"))
    else:
        num_gpus = 0
    worker.local_scheduler_client = ray.local_scheduler.LocalSchedulerClient(
        info["local_scheduler_socket_name"], worker.worker_id, worker.actor_id,
        is_worker, num_gpus)

    # If this is a driver, set the current task ID, the task driver ID, and set
    # the task index to 0.
    if mode in [SCRIPT_MODE, SILENT_MODE]:
        # If the user provided an object_id_seed, then set the current task ID
        # deterministically based on that seed (without altering the state of
        # the user's random number generator). Otherwise, set the current task
        # ID randomly to avoid object ID collisions.
        numpy_state = np.random.get_state()
        if object_id_seed is not None:
            np.random.seed(object_id_seed)
        else:
            # Try to use true randomness.
            np.random.seed(None)
        worker.current_task_id = ray.local_scheduler.ObjectID(
            np.random.bytes(20))
        # When tasks are executed on remote workers in the context of multiple
        # drivers, the task driver ID is used to keep track of which driver is
        # responsible for the task so that error messages will be propagated to
        # the correct driver.
        worker.task_driver_id = ray.local_scheduler.ObjectID(worker.worker_id)
        # Reset the state of the numpy random number generator.
        np.random.set_state(numpy_state)
        # Set other fields needed for computing task IDs.
        worker.task_index = 0
        worker.put_index = 0

        # Create an entry for the driver task in the task table. This task is
        # added immediately with status RUNNING. This allows us to push errors
        # related to this driver task back to the driver.  For example, if the
        # driver creates an object that is later evicted, we should notify the
        # user that we're unable to reconstruct the object, since we cannot
        # rerun the driver.
        nil_actor_counter = 0
        driver_task = ray.local_scheduler.Task(
            worker.task_driver_id,
            ray.local_scheduler.ObjectID(NIL_FUNCTION_ID),
            [],
            0,
            worker.current_task_id,
            worker.task_index,
            ray.local_scheduler.ObjectID(NIL_ACTOR_ID),
            ray.local_scheduler.ObjectID(NIL_ACTOR_ID),
            nil_actor_counter,
            False,
            [],
            {"CPU": 0})
        global_state._execute_command(
            driver_task.task_id(),
            "RAY.TASK_TABLE_ADD",
            driver_task.task_id().id(),
            TASK_STATUS_RUNNING,
            NIL_LOCAL_SCHEDULER_ID,
            driver_task.execution_dependencies_string(),
            0,
            ray.local_scheduler.task_to_string(driver_task))
        # Set the driver's current task ID to the task ID assigned to the
        # driver task.
        worker.current_task_id = driver_task.task_id()

    # If this is an actor, get the ID of the corresponding class for the actor.
    if worker.actor_id != NIL_ACTOR_ID:
        actor_key = b"Actor:" + worker.actor_id
        class_id = worker.redis_client.hget(actor_key, "class_id")
        worker.class_id = class_id

    # Initialize the serialization library. This registers some classes, and so
    # it must be run before we export all of the cached remote functions.
    _initialize_serialization()

    # Start a thread to import exports from the driver or from other workers.
    # Note that the driver also has an import thread, which is used only to
    # import custom class definitions from calls to register_custom_serializer
    # that happen under the hood on workers.
    t = threading.Thread(target=import_thread, args=(worker, mode))
    # Making the thread a daemon causes it to exit when the main thread exits.
    t.daemon = True
    t.start()

    # If this is a driver running in SCRIPT_MODE, start a thread to print error
    # messages asynchronously in the background. Ideally the scheduler would
    # push messages to the driver's worker service, but we ran into bugs when
    # trying to properly shutdown the driver's worker service, so we are
    # temporarily using this implementation which constantly queries the
    # scheduler for new error messages.
    if mode == SCRIPT_MODE:
        t = threading.Thread(target=print_error_messages, args=(worker,))
        # Making the thread a daemon causes it to exit when the main thread
        # exits.
        t.daemon = True
        t.start()

    if mode in [SCRIPT_MODE, SILENT_MODE]:
        # Add the directory containing the script that is running to the Python
        # paths of the workers. Also add the current directory. Note that this
        # assumes that the directory structures on the machines in the clusters
        # are the same.
        script_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
        current_directory = os.path.abspath(os.path.curdir)
        worker.run_function_on_all_workers(
            lambda worker_info: sys.path.insert(1, script_directory))
        worker.run_function_on_all_workers(
            lambda worker_info: sys.path.insert(1, current_directory))
        # TODO(rkn): Here we first export functions to run, then remote
        # functions. The order matters. For example, one of the functions to
        # run may set the Python path, which is needed to import a module used
        # to define a remote function. We may want to change the order to
        # simply be the order in which the exports were defined on the driver.
        # In addition, we will need to retain the ability to decide what the
        # first few exports are (mostly to set the Python path). Additionally,
        # note that the first exports to be defined on the driver will be the
        # ones defined in separate modules that are imported by the driver.
        # Export cached functions_to_run.
        for function in worker.cached_functions_to_run:
            worker.run_function_on_all_workers(function)
        # Export cached remote functions to the workers.
        for cached_type, info in worker.cached_remote_functions_and_actors:
            if cached_type == "remote_function":
                (function_id, func_name, func,
                 func_invoker, function_properties) = info
                export_remote_function(function_id, func_name, func,
                                       func_invoker, function_properties,
                                       worker)
            elif cached_type == "actor":
                (key, actor_class_info) = info
                ray.actor.publish_actor_class_to_key(key, actor_class_info,
                                                     worker)
            else:
                assert False, "This code should be unreachable."
    worker.cached_functions_to_run = None
    worker.cached_remote_functions_and_actors = None
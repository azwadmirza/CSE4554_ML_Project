def fetch_and_execute_function_to_run(key, worker=global_worker):
    """Run on arbitrary function on the worker."""
    driver_id, serialized_function = worker.redis_client.hmget(
        key, ["driver_id", "function"])

    if (worker.mode in [SCRIPT_MODE, SILENT_MODE] and
            driver_id != worker.task_driver_id.id()):
        # This export was from a different driver and there's no need for this
        # driver to import it.
        return

    try:
        # Deserialize the function.
        function = pickle.loads(serialized_function)
        # Run the function.
        function({"worker": worker})
    except Exception:
        # If an exception was thrown when the function was run, we record the
        # traceback and notify the scheduler of the failure.
        traceback_str = traceback.format_exc()
        # Log the error message.
        name = function.__name__ if ("function" in locals() and
                                     hasattr(function, "__name__")) else ""
        ray.utils.push_error_to_driver(worker.redis_client,
                                       "function_to_run",
                                       traceback_str,
                                       driver_id=driver_id,
                                       data={"name": name})
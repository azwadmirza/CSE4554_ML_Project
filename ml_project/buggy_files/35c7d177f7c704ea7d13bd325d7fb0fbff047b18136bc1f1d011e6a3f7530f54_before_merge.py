def custom_excepthook(type, value, tb):
    # If this is a driver, push the exception to GCS worker table.
    if global_worker.mode == SCRIPT_MODE:
        error_message = "".join(traceback.format_tb(tb))
        worker_id = global_worker.worker_id
        worker_type = ray.gcs_utils.DRIVER
        worker_info = {"exception": error_message}

        ray.state.state.add_worker(worker_id, worker_type, worker_info)
    # Call the normal excepthook.
    normal_excepthook(type, value, tb)
def _flush_queue():
    """
    Flush the metric queue and log contents in batches to MLflow.
    Queue is divided into batches according to run id.
    """
    global _metric_queue
    try:
        client = mlflow.tracking.MlflowClient()
        dic = _assoc_list_to_map(_metric_queue)
        for key in dic:
            client.log_batch(key, metrics=dic[key], params=[], tags=[])
    except MlflowException as e:
        warnings.warn("Logging to MLflow failed: " + str(e))
    finally:
        _metric_queue = []
def _log_artifacts_with_warning(**kwargs):
    try_mlflow_log(mlflow.log_artifacts, **kwargs)
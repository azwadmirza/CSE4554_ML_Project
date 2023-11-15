def _log_artifacts_with_warning(**kwargs):
    try:
        mlflow.log_artifacts(**kwargs)
    except MlflowException as e:
        warnings.warn("Logging to MLflow failed: " + str(e))
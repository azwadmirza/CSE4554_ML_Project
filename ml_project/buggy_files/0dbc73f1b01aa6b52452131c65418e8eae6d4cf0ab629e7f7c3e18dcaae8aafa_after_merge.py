  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]):
    """Overrides the tfx_pusher_executor.

    Args:
      input_dict: Input dict from input key to a list of artifacts, including:
        - model_export: exported model from trainer.
        - model_blessing: model blessing path from model_validator.
      output_dict: Output dict from key to a list of artifacts, including:
        - model_push: A list of 'ModelPushPath' artifact of size one. It will
          include the model in this push execution if the model was pushed.
      exec_properties: Mostly a passthrough input dict for
        tfx.components.Pusher.executor.  custom_config.bigquery_serving_args is
        consumed by this class.  For the full set of parameters supported by
        Big Query ML, refer to https://cloud.google.com/bigquery-ml/

    Returns:
      None
    Raises:
      ValueError:
        If bigquery_serving_args is not in exec_properties.custom_config.
        If pipeline_root is not 'gs://...'
      RuntimeError: if the Big Query job failed.
    """
    self._log_startup(input_dict, output_dict, exec_properties)
    model_push = artifact_utils.get_single_instance(
        output_dict[tfx_pusher_executor.PUSHED_MODEL_KEY])
    if not self.CheckBlessing(input_dict):
      self._MarkNotPushed(model_push)
      return

    model_export = artifact_utils.get_single_instance(
        input_dict[tfx_pusher_executor.MODEL_KEY])
    model_export_uri = model_export.uri

    custom_config = exec_properties.get(_CUSTOM_CONFIG_KEY, {})
    bigquery_serving_args = custom_config.get(SERVING_ARGS_KEY)
    # if configuration is missing error out
    if bigquery_serving_args is None:
      raise ValueError('Big Query ML configuration was not provided')

    bq_model_uri = '.'.join([
        bigquery_serving_args[_PROJECT_ID_KEY],
        bigquery_serving_args[_BQ_DATASET_ID_KEY],
        bigquery_serving_args[_MODEL_NAME_KEY],
    ])

    # Deploy the model.
    io_utils.copy_dir(
        src=path_utils.serving_model_path(model_export_uri),
        dst=model_push.uri)
    model_path = model_push.uri
    if not model_path.startswith(_GCS_PREFIX):
      raise ValueError(
          'pipeline_root must be gs:// for BigQuery ML Pusher.')

    logging.info('Deploying the model to BigQuery ML for serving: %s from %s',
                 bigquery_serving_args, model_path)

    query = _BQML_CREATE_OR_REPLACE_MODEL_QUERY_TEMPLATE.format(
        model_uri=bq_model_uri, model_path=model_path)

    # TODO(zhitaoli): Refactor the executor_class_path creation into a common
    # utility function.
    executor_class_path = '%s.%s' % (self.__class__.__module__,
                                     self.__class__.__name__)
    with telemetry_utils.scoped_labels(
        {telemetry_utils.TFX_EXECUTOR: executor_class_path}):
      default_query_job_config = bigquery.job.QueryJobConfig(
          labels=telemetry_utils.get_labels_dict())
    client = bigquery.Client(default_query_job_config=default_query_job_config)

    try:
      query_job = client.query(query)
      query_job.result()  # Waits for the query to finish
    except Exception as e:
      raise RuntimeError('BigQuery ML Push failed: {}'.format(e))

    logging.info('Successfully deployed model %s serving from %s',
                 bq_model_uri, model_path)

    # Setting the push_destination to bigquery uri
    self._MarkPushed(model_push, pushed_destination=bq_model_uri)
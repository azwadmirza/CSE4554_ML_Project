def deploy_model_for_aip_prediction(
    serving_path: Text,
    model_version: Text,
    ai_platform_serving_args: Dict[Text, Any],
    executor_class_path: Text,
):
  """Deploys a model for serving with AI Platform.

  Args:
    serving_path: The path to the model. Must be a GCS URI.
    model_version: Version of the model being deployed. Must be different from
      what is currently being served.
    ai_platform_serving_args: Dictionary containing arguments for pushing to AI
      Platform. For the full set of parameters supported, refer to
      https://cloud.google.com/ml-engine/reference/rest/v1/projects.models.versions#Version
    executor_class_path: class path for TFX core default trainer.

  Raises:
    RuntimeError: if an error is encountered when trying to push.
  """
  absl.logging.info(
      'Deploying to model with version {} to AI Platform for serving: {}'
      .format(model_version, ai_platform_serving_args))

  model_name = ai_platform_serving_args['model_name']
  project_id = ai_platform_serving_args['project_id']
  regions = ai_platform_serving_args.get('regions', [])
  runtime_version = _get_tf_runtime_version(tf.__version__)
  python_version = _get_caip_python_version(runtime_version)

  api = discovery.build('ml', 'v1')
  body = {'name': model_name, 'regions': regions}
  parent = 'projects/{}'.format(project_id)
  try:
    api.projects().models().create(body=body, parent=parent).execute()
  except errors.HttpError as e:
    # If the error is to create an already existing model, it's ok to ignore.
    # TODO(b/135211463): Remove the disable once the pytype bug is fixed.
    if e.resp.status == 409:  # pytype: disable=attribute-error
      absl.logging.warn('Model {} already exists'.format(model_name))
    else:
      raise RuntimeError('AI Platform Push failed: {}'.format(e))
  with telemetry_utils.scoped_labels(
      {telemetry_utils.TFX_EXECUTOR: executor_class_path}):
    job_labels = telemetry_utils.get_labels_dict()
  body = {
      'name': model_version,
      'deployment_uri': serving_path,
      'runtime_version': runtime_version,
      'python_version': python_version,
      'labels': job_labels,
  }

  # Push to AIP, and record the operation name so we can poll for its state.
  model_name = 'projects/{}/models/{}'.format(project_id, model_name)
  response = api.projects().models().versions().create(
      body=body, parent=model_name).execute()
  op_name = response['name']

  while True:
    deploy_status = api.projects().operations().get(name=op_name).execute()
    if deploy_status.get('done'):
      # Set the new version as default.
      api.projects().models().versions().setDefault(
          name='{}/versions/{}'.format(model_name, deploy_status['response']
                                       ['name'])).execute()
      break
    if 'error' in deploy_status:
      # The operation completed with an error.
      absl.logging.error(deploy_status['error'])
      raise RuntimeError(
          'Failed to deploy model to AI Platform for serving: {}'.format(
              deploy_status['error']))

    time.sleep(_POLLING_INTERVAL_IN_SECONDS)
    absl.logging.info('Model still being deployed...')

  absl.logging.info(
      'Successfully deployed model {} with version {}, serving from {}'.format(
          model_name, model_version, serving_path))
def deploy_model_for_cmle_serving(serving_path: Text, model_version: Text,
                                  cmle_serving_args: Dict[Text, Any]):
  """Deploys a model for serving with CMLE.

  Args:
    serving_path: The path to the model. Must be a GCS URI.
    model_version: Version of the model being deployed. Must be different from
      what is currently being served.
    cmle_serving_args: Dictionary containing arguments for pushing to CMLE. For
      the full set of parameters supported, refer to
      https://cloud.google.com/ml-engine/reference/rest/v1/projects.models.versions#Version

  Raises:
    RuntimeError: if an error is encountered when trying to push.
  """
  tf.logging.info(
      'Deploying to model with version {} to CMLE for serving: {}'.format(
          model_version, cmle_serving_args))

  model_name = cmle_serving_args['model_name']
  project_id = cmle_serving_args['project_id']
  runtime_version = _get_tf_runtime_version()
  python_version = _get_caip_python_version()

  api = discovery.build('ml', 'v1')
  body = {'name': model_name}
  parent = 'projects/{}'.format(project_id)
  try:
    api.projects().models().create(body=body, parent=parent).execute()
  except errors.HttpError as e:
    # If the error is to create an already existing model, it's ok to ignore.
    # TODO(b/135211463): Remove the disable once the pytype bug is fixed.
    if e.resp.status == 409:  # pytype: disable=attribute-error
      tf.logging.warn('Model {} already exists'.format(model_name))
    else:
      raise RuntimeError('CMLE Push failed: {}'.format(e))

  body = {
      'name': 'v{}'.format(model_version),
      'deployment_uri': serving_path,
      'runtime_version': runtime_version,
      'python_version': python_version,
  }

  # Push to CMLE, and record the operation name so we can poll for its state.
  model_name = 'projects/{}/models/{}'.format(project_id, model_name)
  response = api.projects().models().versions().create(
      body=body, parent=model_name).execute()
  op_name = response['name']

  while True:
    deploy_status = api.projects().operations().get(name=op_name).execute()
    if deploy_status.get('done'):
      break
    if 'error' in deploy_status:
      # The operation completed with an error.
      tf.logging.error(deploy_status['error'])
      raise RuntimeError(
          'Failed to deploy model to CMLE for serving: {}'.format(
              deploy_status['error']))

    time.sleep(_POLLING_INTERVAL_IN_SECONDS)
    tf.logging.info('Model still being deployed...')

  tf.logging.info(
      'Successfully deployed model {} with version {}, serving from {}'.format(
          model_name, model_version, serving_path))
  def create_run_from_pipeline_package(self, pipeline_file: str, arguments: Mapping[str, str], run_name=None, experiment_name=None, namespace=None):
    '''Runs pipeline on KFP-enabled Kubernetes cluster.
    This command compiles the pipeline function, creates or gets an experiment and submits the pipeline for execution.

    Args:
      pipeline_file: A compiled pipeline package file.
      arguments: Arguments to the pipeline function provided as a dict.
      run_name: Optional. Name of the run to be shown in the UI.
      experiment_name: Optional. Name of the experiment to add the run to.
      namespace: kubernetes namespace where the pipeline runs are created.
        For single user deployment, leave it as None;
        For multi user, input a namespace where the user is authorized
    '''

    class RunPipelineResult:
      def __init__(self, client, run_info):
        self._client = client
        self.run_info = run_info
        self.run_id = run_info.id

      def wait_for_run_completion(self, timeout=None):
        timeout = timeout or datetime.datetime.max - datetime.datetime.min
        return self._client.wait_for_run_completion(self.run_id, timeout)

      def __repr__(self):
        return 'RunPipelineResult(run_id={})'.format(self.run_id)

    #TODO: Check arguments against the pipeline function
    pipeline_name = os.path.basename(pipeline_file)
    experiment_name = experiment_name or os.environ.get(KF_PIPELINES_DEFAULT_EXPERIMENT_NAME, None)
    overridden_experiment_name = os.environ.get(KF_PIPELINES_OVERRIDE_EXPERIMENT_NAME, experiment_name)
    if overridden_experiment_name != experiment_name:
      import warnings
      warnings.warn('Changing experiment name from "{}" to "{}".'.format(experiment_name, overridden_experiment_name))
    experiment_name = overridden_experiment_name or 'Default'
    run_name = run_name or pipeline_name + ' ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    experiment = self.create_experiment(name=experiment_name, namespace=namespace)
    run_info = self.run_pipeline(experiment.id, run_name, pipeline_file, arguments)
    return RunPipelineResult(self, run_info)
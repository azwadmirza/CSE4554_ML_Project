  def create_run_from_pipeline_func(self, pipeline_func: Callable, arguments: Mapping[str, str], run_name=None, experiment_name=None, pipeline_conf: kfp.dsl.PipelineConf = None, namespace=None):
    '''Runs pipeline on KFP-enabled Kubernetes cluster.
    This command compiles the pipeline function, creates or gets an experiment and submits the pipeline for execution.

    Args:
      pipeline_func: A function that describes a pipeline by calling components and composing them into execution graph.
      arguments: Arguments to the pipeline function provided as a dict.
      run_name: Optional. Name of the run to be shown in the UI.
      experiment_name: Optional. Name of the experiment to add the run to.
      namespace: kubernetes namespace where the pipeline runs are created.
        For single user deployment, leave it as None;
        For multi user, input a namespace where the user is authorized
    '''
    #TODO: Check arguments against the pipeline function
    pipeline_name = pipeline_func.__name__
    run_name = run_name or pipeline_name + ' ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    with tempfile.TemporaryDirectory() as tmpdir:
      pipeline_package_path = os.path.join(tmpdir, 'pipeline.yaml')
      compiler.Compiler().compile(pipeline_func, pipeline_package_path, pipeline_conf=pipeline_conf)
      return self.create_run_from_pipeline_package(pipeline_package_path, arguments, run_name, experiment_name, namespace)
def build_importer_spec(
    input_type_schema: str,
    pipeline_param_name: Optional[str] = None,
    constant_value: Optional[str] = None
) -> pipeline_spec_pb2.PipelineDeploymentConfig.ImporterSpec:
  """Builds an importer executor spec.

  Args:
    input_type_schema: The type of the input artifact.
    pipeline_param_name: The name of the pipeline parameter if the importer gets
      its artifacts_uri via a pipeline parameter. This argument is mutually
      exclusive with constant_value.
    constant_value: The value of artifact_uri in case a contant value is passed
      directly into the compoent op. This argument is mutually exclusive with
      pipeline_param_name.

  Returns:
    An importer spec.
  """
  assert bool(pipeline_param_name is None) != bool(constant_value is None), (
      'importer spec should be built using either pipeline_param_name or '
      'constant_value.')
  importer_spec = pipeline_spec_pb2.PipelineDeploymentConfig.ImporterSpec()
  importer_spec.type_schema.instance_schema = input_type_schema
  # TODO: subject to IR change on artifact_uri message type.
  if pipeline_param_name:
    importer_spec.artifact_uri.runtime_parameter = pipeline_param_name
  elif constant_value:
    importer_spec.artifact_uri.constant_value.string_value = constant_value
  return importer_spec
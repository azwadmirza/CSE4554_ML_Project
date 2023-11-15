def _attach_v2_specs(
    task: _container_op.ContainerOp,
    component_spec: _structures.ComponentSpec,
    arguments: Mapping[str, Any],
) -> None:
  """Attaches v2 specs to a ContainerOp object.

    Args:
      task: The ContainerOp object to attach IR specs.
      component_spec: The component spec object.
      arguments: The dictionary of component arguments.
  """

  # Attach v2_specs to the ContainerOp object regardless whether the pipeline is
  # being compiled to v1 (Argo yaml) or v2 (IR json).
  # However, there're different behaviors for the two cases. Namely, resolved
  # commands and arguments, error handling, etc.
  # Regarding the difference in error handling, v2 has a stricter requirement on
  # input type annotation. For instance, an input without any type annotation is
  # viewed as an artifact, and if it's paired with InputValuePlaceholder, an
  # error will be thrown at compile time. However, we cannot raise such an error
  # in v1, as it wouldn't break existing pipelines.
  is_compiling_for_v2 = False
  for frame in inspect.stack():
    if '_create_pipeline_v2' in frame:
      is_compiling_for_v2 = True
      break

  def _resolve_commands_and_args_v2(
      component_spec: _structures.ComponentSpec,
      arguments: Mapping[str, Any],
  ) -> _components._ResolvedCommandLineAndPaths:
    """Resolves the command line argument placeholders for v2 (IR).

    Args:
      component_spec: The component spec object.
      arguments: The dictionary of component arguments.

    Returns:
      A named tuple: _components._ResolvedCommandLineAndPaths.
    """
    inputs_dict = {
        input_spec.name: input_spec
        for input_spec in component_spec.inputs or []
    }
    outputs_dict = {
        output_spec.name: output_spec
        for output_spec in component_spec.outputs or []
    }

    def _input_artifact_uri_placeholder(input_key: str) -> str:
      if is_compiling_for_v2 and type_utils.is_parameter_type(
          inputs_dict[input_key].type):
        raise TypeError('Input "{}" with type "{}" cannot be paired with '
                        'InputUriPlaceholder.'.format(
                            input_key, inputs_dict[input_key].type))
      else:
        return "{{{{$.inputs.artifacts['{}'].uri}}}}".format(input_key)

    def _input_artifact_path_placeholder(input_key: str) -> str:
      if is_compiling_for_v2 and type_utils.is_parameter_type(
          inputs_dict[input_key].type):
        raise TypeError('Input "{}" with type "{}" cannot be paired with '
                        'InputPathPlaceholder.'.format(
                            input_key, inputs_dict[input_key].type))
      elif is_compiling_for_v2 and input_key in importer_specs:
        raise TypeError(
            'Input "{}" with type "{}" is not connected to any upstream output. '
            'However it is used with InputPathPlaceholder. '
            'If you want to import an existing artifact using a system-connected'
            ' importer node, use InputUriPlaceholder instead. '
            'Or if you just want to pass a string parameter, use string type and'
            ' InputValuePlaceholder instead.'.format(
                input_key, inputs_dict[input_key].type))
      else:
        return "{{{{$.inputs.artifacts['{}'].path}}}}".format(input_key)

    def _input_parameter_placeholder(input_key: str) -> str:
      if is_compiling_for_v2 and not type_utils.is_parameter_type(
          inputs_dict[input_key].type):
        raise TypeError('Input "{}" with type "{}" cannot be paired with '
                        'InputValuePlaceholder.'.format(
                            input_key, inputs_dict[input_key].type))
      else:
        return "{{{{$.inputs.parameters['{}']}}}}".format(input_key)

    def _output_artifact_uri_placeholder(output_key: str) -> str:
      if is_compiling_for_v2 and type_utils.is_parameter_type(
          outputs_dict[output_key].type):
        raise TypeError('Output "{}" with type "{}" cannot be paired with '
                        'OutputUriPlaceholder.'.format(
                            output_key, outputs_dict[output_key].type))
      else:
        return "{{{{$.outputs.artifacts['{}'].uri}}}}".format(output_key)

    def _output_artifact_path_placeholder(output_key: str) -> str:
      return "{{{{$.outputs.artifacts['{}'].path}}}}".format(output_key)

    def _output_parameter_path_placeholder(output_key: str) -> str:
      return "{{{{$.outputs.parameters['{}'].output_file}}}}".format(output_key)

    def _resolve_output_path_placeholder(output_key: str) -> str:
      if type_utils.is_parameter_type(outputs_dict[output_key].type):
        return _output_parameter_path_placeholder(output_key)
      else:
        return _output_artifact_path_placeholder(output_key)

    resolved_cmd = _components._resolve_command_line_and_paths(
        component_spec=component_spec,
        arguments=arguments,
        input_value_generator=_input_parameter_placeholder,
        input_uri_generator=_input_artifact_uri_placeholder,
        output_uri_generator=_output_artifact_uri_placeholder,
        input_path_generator=_input_artifact_path_placeholder,
        output_path_generator=_resolve_output_path_placeholder,
    )
    return resolved_cmd

  pipeline_task_spec = pipeline_spec_pb2.PipelineTaskSpec()

  # Keep track of auto-injected importer spec.
  importer_specs = {}

  # Check types of the reference arguments and serialize PipelineParams
  original_arguments = arguments
  arguments = arguments.copy()

  # Preserver input params for ContainerOp.inputs
  input_params = list(
      set([
          param for param in arguments.values()
          if isinstance(param, _pipeline_param.PipelineParam)
      ]))

  for input_name, argument_value in arguments.items():
    if isinstance(argument_value, _pipeline_param.PipelineParam):
      input_type = component_spec._inputs_dict[input_name].type
      reference_type = argument_value.param_type
      types.verify_type_compatibility(
          reference_type, input_type,
          'Incompatible argument passed to the input "{}" of component "{}": '
          .format(input_name, component_spec.name))

      arguments[input_name] = str(argument_value)

      if type_utils.is_parameter_type(input_type):
        if argument_value.op_name:
          pipeline_task_spec.inputs.parameters[
              input_name].task_output_parameter.producer_task = (
                  dsl_utils.sanitize_task_name(argument_value.op_name))
          pipeline_task_spec.inputs.parameters[
              input_name].task_output_parameter.output_parameter_key = (
                  argument_value.name)
        else:
          pipeline_task_spec.inputs.parameters[
              input_name].component_input_parameter = argument_value.name
      else:
        if argument_value.op_name:
          pipeline_task_spec.inputs.artifacts[
              input_name].task_output_artifact.producer_task = (
                  dsl_utils.sanitize_task_name(argument_value.op_name))
          pipeline_task_spec.inputs.artifacts[
              input_name].task_output_artifact.output_artifact_key = (
                  argument_value.name)
        elif is_compiling_for_v2:
          # argument_value.op_name could be none, in which case an importer node
          # will be inserted later.
          # Importer node is only applicable for v2 engine.
          pipeline_task_spec.inputs.artifacts[
              input_name].task_output_artifact.producer_task = ''
          type_schema = type_utils.get_input_artifact_type_schema(
              input_name, component_spec.inputs)
          importer_specs[input_name] = importer_node.build_importer_spec(
              input_type_schema=type_schema,
              pipeline_param_name=argument_value.name)
    elif isinstance(argument_value, str):
      pipeline_params = _pipeline_param.extract_pipelineparams_from_any(
          argument_value)
      if pipeline_params and is_compiling_for_v2:
        # argument_value contains PipelineParam placeholders.
        raise NotImplementedError(
            'Currently, a component input can only accept either a constant '
            'value or a reference to another pipeline parameter. It cannot be a '
            'combination of both. Got: {} for input {}'.format(
                argument_value, input_name))

      input_type = component_spec._inputs_dict[input_name].type
      if type_utils.is_parameter_type(input_type):
        pipeline_task_spec.inputs.parameters[
            input_name].runtime_value.constant_value.string_value = (
                argument_value)
      elif is_compiling_for_v2:
        # An importer node with constant value artifact_uri will be inserted.
        # Importer node is only applicable for v2 engine.
        pipeline_task_spec.inputs.artifacts[
            input_name].task_output_artifact.producer_task = ''
        type_schema = type_utils.get_input_artifact_type_schema(
            input_name, component_spec.inputs)
        importer_specs[input_name] = importer_node.build_importer_spec(
            input_type_schema=type_schema, constant_value=argument_value)
    elif isinstance(argument_value, int):
      pipeline_task_spec.inputs.parameters[
          input_name].runtime_value.constant_value.int_value = argument_value
    elif isinstance(argument_value, float):
      pipeline_task_spec.inputs.parameters[
          input_name].runtime_value.constant_value.double_value = argument_value
    elif isinstance(argument_value, _container_op.ContainerOp):
      raise TypeError(
          'ContainerOp object {} was passed to component as an input argument. '
          'Pass a single output instead.'.format(input_name))
    else:
      if is_compiling_for_v2:
        raise NotImplementedError(
            'Input argument supports only the following types: PipelineParam'
            ', str, int, float. Got: "{}".'.format(argument_value))

  if not component_spec.name:
    component_spec.name = _components._default_component_name

  # task.name is unique at this point.
  pipeline_task_spec.task_info.name = (dsl_utils.sanitize_task_name(task.name))
  pipeline_task_spec.component_ref.name = (
      dsl_utils.sanitize_component_name(component_spec.name))

  task.task_spec = pipeline_task_spec
  task.importer_specs = importer_specs
  task.component_spec = dsl_component_spec.build_component_spec_from_structure(
      component_spec)

  resolved_cmd = _resolve_commands_and_args_v2(
      component_spec=component_spec, arguments=original_arguments)

  task.container_spec = (
      pipeline_spec_pb2.PipelineDeploymentConfig.PipelineContainerSpec(
          image=component_spec.implementation.container.image,
          command=resolved_cmd.command,
          args=resolved_cmd.args))

  # Override command and arguments if compiling to v2.
  if is_compiling_for_v2:
    task.command = resolved_cmd.command
    task.arguments = resolved_cmd.args

    # limit this to v2 compiling only to avoid possible behavior change in v1.
    task.inputs = input_params
def build_python_component(component_func, target_image, base_image=None, dependency=[], staging_gcs_path=None, timeout=600, namespace=None, target_component_file=None, python_version='python3'):
  """build_component automatically builds a container image for the component_func based on the base_image and pushes to the target_image.

  Args:
    component_func (python function): The python function to build components upon
    base_image (str): Docker image to use as a base image
    target_image (str): Full URI to push the target image
    staging_gcs_path (str): GCS blob that can store temporary build files
    target_image (str): target image path
    timeout (int): the timeout for the image build(in secs), default is 600 seconds
    namespace (str): the namespace within which to run the kubernetes kaniko job. If the
    job is running on GKE and value is None the underlying functions will use the default namespace from GKE.  .
    dependency (list): a list of VersionedDependency, which includes the package name and versions, default is empty
    python_version (str): choose python2 or python3, default is python3

  Raises:
    ValueError: The function is not decorated with python_component decorator or the python_version is neither python2 nor python3
  """

  _configure_logger(logging.getLogger())

  if component_func is None:
    raise ValueError('component_func must not be None')
  if target_image is None:
    raise ValueError('target_image must not be None')

  if python_version not in ['python2', 'python3']:
    raise ValueError('python_version has to be either python2 or python3')

  if staging_gcs_path is None:
    raise ValueError('staging_gcs_path must not be None')

  if base_image is None:
    base_image = getattr(component_func, '_component_base_image', None)
  if base_image is None:
    from ..components._python_op import default_base_image_or_builder
    base_image = default_base_image_or_builder
    if isinstance(base_image, Callable):
      base_image = base_image()

  logging.info('Build an image that is based on ' +
                                  base_image +
                                  ' and push the image to ' +
                                  target_image)

  component_spec = _func_to_component_spec(component_func, base_image=base_image)
  command_line_args = component_spec.implementation.container.command

  program_launcher_index = command_line_args.index('program_path=$(mktemp)\necho -n "$0" > "$program_path"\npython3 -u "$program_path" "$@"\n')
  assert program_launcher_index in [2, 3]

  program_code_index = program_launcher_index + 1
  program_code = command_line_args[program_code_index]
  program_rel_path = 'ml/main.py'
  program_container_path = '/' + program_rel_path

  # Replacing the inline code with calling a local program
  # Before: sh -ec '... && python3 -u ...' 'import sys ...' --param1 ...
  # After:  python3 -u main.py --param1 ...
  command_line_args[program_code_index] = program_container_path
  command_line_args.pop(program_launcher_index)
  command_line_args[program_launcher_index - 1] = '-u'  # -ec => -u
  command_line_args[program_launcher_index - 2] = python_version  # sh => python3

  if python_version == 'python2':
    import warnings
    warnings.warn('Python2 is not longer supported')

  arc_docker_filename = 'Dockerfile'
  arc_requirement_filename = 'requirements.txt'

  with tempfile.TemporaryDirectory() as local_build_dir:
    # Write the program code to a file in the context directory
    local_python_filepath = os.path.join(local_build_dir, program_rel_path)
    os.makedirs(os.path.dirname(local_python_filepath), exist_ok=True)
    with open(local_python_filepath, 'w') as f:
      f.write(program_code)

    # Generate the python package requirements file in the context directory
    local_requirement_filepath = os.path.join(local_build_dir, arc_requirement_filename)
    _dependency_to_requirements(dependency, local_requirement_filepath)

    # Generate Dockerfile in the context directory
    local_docker_filepath = os.path.join(local_build_dir, arc_docker_filename)
    _generate_dockerfile(local_docker_filepath, base_image, python_version, arc_requirement_filename, add_files={program_rel_path: program_container_path})

    logging.info('Building and pushing container image.')
    container_builder = ContainerBuilder(staging_gcs_path, target_image, namespace)
    image_name_with_digest = container_builder.build(local_build_dir, arc_docker_filename, target_image, timeout)

  component_spec.implementation.container.image = image_name_with_digest

  # Optionally writing the component definition to a local file for sharing
  target_component_file = target_component_file or getattr(component_func, '_component_target_component_file', None)
  if target_component_file:
    component_spec.save(target_component_file)

  task_factory_function = _create_task_factory_from_component_spec(component_spec)
  return task_factory_function
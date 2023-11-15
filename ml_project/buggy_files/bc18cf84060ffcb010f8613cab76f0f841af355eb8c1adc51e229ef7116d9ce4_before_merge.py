def _func_to_component_spec(func, extra_code='', base_image : str = None, packages_to_install: List[str] = None, modules_to_capture: List[str] = None, use_code_pickling=False) -> ComponentSpec:
    '''Takes a self-contained python function and converts it to component.

    Args:
        func: Required. The function to be converted
        base_image: Optional. Docker image to be used as a base image for the python component. Must have python 3.5+ installed. Default is python:3.7
                    Note: The image can also be specified by decorating the function with the @python_component decorator. If different base images are explicitly specified in both places, an error is raised.
        extra_code: Optional. Python source code that gets placed before the function code. Can be used as workaround to define types used in function signature.
        packages_to_install: Optional. List of [versioned] python packages to pip install before executing the user function.
        modules_to_capture: Optional. List of module names that will be captured (instead of just referencing) during the dependency scan. By default the :code:`func.__module__` is captured.
        use_code_pickling: Specifies whether the function code should be captured using pickling as opposed to source code manipulation. Pickling has better support for capturing dependencies, but is sensitive to version mismatch between python in component creation environment and runtime image.

    Returns:
        A :py:class:`kfp.components.structures.ComponentSpec` instance.
    '''
    decorator_base_image = getattr(func, '_component_base_image', None)
    if decorator_base_image is not None:
        if base_image is not None and decorator_base_image != base_image:
            raise ValueError('base_image ({}) conflicts with the decorator-specified base image metadata ({})'.format(base_image, decorator_base_image))
        else:
            base_image = decorator_base_image
    else:
        if base_image is None:
            base_image = default_base_image_or_builder
            if isinstance(base_image, Callable):
                base_image = base_image()

    packages_to_install = packages_to_install or []

    component_spec = _extract_component_interface(func)

    component_inputs = component_spec.inputs or []
    component_outputs = component_spec.outputs or []

    arguments = []
    arguments.extend(InputValuePlaceholder(input.name) for input in component_inputs)
    arguments.extend(OutputPathPlaceholder(output.name) for output in component_outputs)

    if use_code_pickling:
        func_code = _capture_function_code_using_cloudpickle(func, modules_to_capture)
        # pip startup is quite slow. TODO: Remove the special cloudpickle installation code in favor of the the following line once a way to speed up pip startup is discovered.
        #packages_to_install.append('cloudpickle==1.1.1')
    else:
        func_code = _capture_function_code_using_source_copy(func)

    definitions = set()
    def get_deserializer_and_register_definitions(type_name):
        deserializer_code = get_deserializer_code_for_type_struct(type_name)
        if deserializer_code:
            (deserializer_code_str, definition_str) = deserializer_code
            if definition_str:
                definitions.add(definition_str)
            return deserializer_code_str
        return 'str'

    pre_func_definitions = set()
    def get_argparse_type_for_input_file(passing_style):
        if passing_style is None:
            return None

        if passing_style is InputPath:
            return 'str'
        elif passing_style is InputTextFile:
            return "argparse.FileType('rt')"
        elif passing_style is InputBinaryFile:
            return "argparse.FileType('rb')"
        # For Output* we cannot use the build-in argparse.FileType objects since they do not create parent directories.
        elif passing_style is OutputPath:
            # ~= return 'str'
            pre_func_definitions.add(inspect.getsource(_make_parent_dirs_and_return_path))
            return _make_parent_dirs_and_return_path.__name__
        elif passing_style is OutputTextFile:
            # ~= return "argparse.FileType('wt')"
            pre_func_definitions.add(inspect.getsource(_parent_dirs_maker_that_returns_open_file))
            return _parent_dirs_maker_that_returns_open_file.__name__ + "('wt')"
        elif passing_style is OutputBinaryFile:
            # ~= return "argparse.FileType('wb')"
            pre_func_definitions.add(inspect.getsource(_parent_dirs_maker_that_returns_open_file))
            return _parent_dirs_maker_that_returns_open_file.__name__ + "('wb')"
        raise NotImplementedError('Unexpected data passing style: "{}".'.format(str(passing_style)))

    def get_serializer_and_register_definitions(type_name) -> str:
        serializer_func = get_serializer_func_for_type_struct(type_name)
        if serializer_func:
            # If serializer is not part of the standard python library, then include its code in the generated program
            if hasattr(serializer_func, '__module__') and not _module_is_builtin_or_standard(serializer_func.__module__):
                import inspect
                serializer_code_str = inspect.getsource(serializer_func)
                definitions.add(serializer_code_str)
            return serializer_func.__name__
        return 'str'

    arg_parse_code_lines = [
        'import argparse',
        '_parser = argparse.ArgumentParser(prog={prog_repr}, description={description_repr})'.format(
            prog_repr=repr(component_spec.name or ''),
            description_repr=repr(component_spec.description or ''),
        ),
    ]
    outputs_passed_through_func_return_tuple = [output for output in component_outputs if output._passing_style is None]
    file_outputs_passed_using_func_parameters = [output for output in component_outputs if output._passing_style is not None]
    arguments = []
    for input in component_inputs + file_outputs_passed_using_func_parameters:
        param_flag = "--" + input.name.replace("_", "-")
        is_required = isinstance(input, OutputSpec) or not input.optional
        line = '_parser.add_argument("{param_flag}", dest="{param_var}", type={param_type}, required={is_required}, default=argparse.SUPPRESS)'.format(
            param_flag=param_flag,
            param_var=input._parameter_name, # Not input.name, since the inputs could have been renamed
            param_type=get_argparse_type_for_input_file(input._passing_style) or get_deserializer_and_register_definitions(input.type),
            is_required=str(is_required),
        )
        arg_parse_code_lines.append(line)

        if input._passing_style in [InputPath, InputTextFile, InputBinaryFile]:
            arguments_for_input = [param_flag, InputPathPlaceholder(input.name)]
        elif input._passing_style in [OutputPath, OutputTextFile, OutputBinaryFile]:
            arguments_for_input = [param_flag, OutputPathPlaceholder(input.name)]
        else:
            arguments_for_input = [param_flag, InputValuePlaceholder(input.name)]

        if is_required:
            arguments.extend(arguments_for_input)
        else:
            arguments.append(
                IfPlaceholder(
                    IfPlaceholderStructure(
                        condition=IsPresentPlaceholder(input.name),
                        then_value=arguments_for_input,
                    )
                )
            )

    if outputs_passed_through_func_return_tuple:
        param_flag="----output-paths"
        output_param_var="_output_paths"
        line = '_parser.add_argument("{param_flag}", dest="{param_var}", type=str, nargs={nargs})'.format(
            param_flag=param_flag,
            param_var=output_param_var,
            nargs=len(outputs_passed_through_func_return_tuple),
        )
        arg_parse_code_lines.append(line)
        arguments.append(param_flag)
        arguments.extend(OutputPathPlaceholder(output.name) for output in outputs_passed_through_func_return_tuple)

    output_serialization_expression_strings = []
    for output in outputs_passed_through_func_return_tuple:
        serializer_call_str = get_serializer_and_register_definitions(output.type)
        output_serialization_expression_strings.append(serializer_call_str)

    pre_func_code = '\n'.join(list(pre_func_definitions))

    arg_parse_code_lines = list(definitions) + arg_parse_code_lines

    arg_parse_code_lines.append(
        '_parsed_args = vars(_parser.parse_args())',
    )
    if outputs_passed_through_func_return_tuple:
        arg_parse_code_lines.append(
            '_output_files = _parsed_args.pop("_output_paths", [])',
        )

    # Putting singular return values in a list to be "zipped" with the serializers and output paths
    outputs_to_list_code = ''
    return_ann = inspect.signature(func).return_annotation
    if ( # The return type is singular, not sequence
        return_ann is not None
        and return_ann != inspect.Parameter.empty
        and not isinstance(return_ann, dict)
        and not hasattr(return_ann, '_fields') # namedtuple
    ):
        outputs_to_list_code = '_outputs = [_outputs]'

    output_serialization_code = ''.join('    {},\n'.format(s) for s in output_serialization_expression_strings)

    full_output_handling_code = '''

{outputs_to_list_code}

_output_serializers = [
{output_serialization_code}
]

import os
for idx, output_file in enumerate(_output_files):
    try:
        os.makedirs(os.path.dirname(output_file))
    except OSError:
        pass
    with open(output_file, 'w') as f:
        f.write(_output_serializers[idx](_outputs[idx]))
'''.format(
        output_serialization_code=output_serialization_code,
        outputs_to_list_code=outputs_to_list_code,
    )

    full_source = \
'''\
{pre_func_code}

{extra_code}

{func_code}

{arg_parse_code}

_outputs = {func_name}(**_parsed_args)
'''.format(
        func_name=func.__name__,
        func_code=func_code,
        pre_func_code=pre_func_code,
        extra_code=extra_code,
        arg_parse_code='\n'.join(arg_parse_code_lines),
    )

    if outputs_passed_through_func_return_tuple:
        full_source += full_output_handling_code

    #Removing consecutive blank lines
    import re
    full_source = re.sub('\n\n\n+', '\n\n', full_source).strip('\n') + '\n'

    package_preinstallation_command = []
    if packages_to_install:
        package_install_command_line = 'PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip install --quiet --no-warn-script-location {}'.format(' '.join([repr(str(package)) for package in packages_to_install]))
        package_preinstallation_command = ['sh', '-c', '({pip_install} || {pip_install} --user) && "$0" "$@"'.format(pip_install=package_install_command_line)]

    component_spec.implementation=ContainerImplementation(
        container=ContainerSpec(
            image=base_image,
            command=package_preinstallation_command + ['python3', '-u', '-c', full_source],
            args=arguments,
        )
    )

    return component_spec
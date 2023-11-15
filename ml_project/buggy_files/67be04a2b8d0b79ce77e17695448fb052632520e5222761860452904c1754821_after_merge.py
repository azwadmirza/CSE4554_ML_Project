def build_command(
    runner,
    job_wrapper,
    container=None,
    modify_command_for_container=True,
    include_metadata=False,
    include_work_dir_outputs=True,
    create_tool_working_directory=True,
    remote_command_params={},
    metadata_directory=None,
):
    """
    Compose the sequence of commands necessary to execute a job. This will
    currently include:

        - environment settings corresponding to any requirement tags
        - preparing input files
        - command line taken from job wrapper
        - commands to set metadata (if include_metadata is True)
    """
    shell = job_wrapper.shell
    base_command_line = job_wrapper.get_command_line()
    # job_id = job_wrapper.job_id
    # log.debug( 'Tool evaluation for job (%s) produced command-line: %s' % ( job_id, base_command_line ) )
    if not base_command_line:
        raise Exception("Attempting to run a tool with empty command definition.")

    commands_builder = CommandsBuilder(base_command_line)

    # All job runners currently handle this case which should never occur
    if not commands_builder.commands:
        return None

    # Version, dependency resolution, and task splitting are prepended to the
    # command - so they need to appear in the following order to ensure that
    # the underlying application used by version command is available in the
    # after dependency resolution but the task splitting command still has
    # Galaxy's Python environment.

    __handle_version_command(commands_builder, job_wrapper)

    # One could imagine also allowing dependencies inside of the container but
    # that is too sophisticated for a first crack at this - build your
    # containers ready to go!
    if not container or container.resolve_dependencies:
        __handle_dependency_resolution(commands_builder, job_wrapper, remote_command_params)

    __handle_task_splitting(commands_builder, job_wrapper)

    if (container and modify_command_for_container) or job_wrapper.commands_in_new_shell:
        if container and modify_command_for_container:
            # Many Docker containers do not have /bin/bash.
            external_command_shell = container.shell
        else:
            external_command_shell = shell
        externalized_commands = __externalize_commands(job_wrapper, external_command_shell, commands_builder, remote_command_params)
        if container and modify_command_for_container:
            # Stop now and build command before handling metadata and copying
            # working directory files back. These should always happen outside
            # of docker container - no security implications when generating
            # metadata and means no need for Galaxy to be available to container
            # and not copying workdir outputs back means on can be more restrictive
            # of where container can write to in some circumstances.
            run_in_container_command = container.containerize_command(
                externalized_commands
            )
            commands_builder = CommandsBuilder( run_in_container_command )
        else:
            commands_builder = CommandsBuilder( externalized_commands )

    # Don't need to create a separate tool working directory for Pulsar
    # jobs - that is handled by Pulsar.
    if create_tool_working_directory:
        # usually working will already exist, but it will not for task
        # split jobs.

        # Remove the working directory incase this is for instance a SLURM re-submission.
        # xref https://github.com/galaxyproject/galaxy/issues/3289
        commands_builder.prepend_command("rm -rf working; mkdir -p working; cd working")

    if include_work_dir_outputs:
        __handle_work_dir_outputs(commands_builder, job_wrapper, runner, remote_command_params)

    commands_builder.capture_return_code()

    if include_metadata and job_wrapper.requires_setting_metadata:
        metadata_directory = metadata_directory or job_wrapper.working_directory
        commands_builder.append_command("cd '%s'" % metadata_directory)
        __handle_metadata(commands_builder, job_wrapper, runner, remote_command_params)

    return commands_builder.build()
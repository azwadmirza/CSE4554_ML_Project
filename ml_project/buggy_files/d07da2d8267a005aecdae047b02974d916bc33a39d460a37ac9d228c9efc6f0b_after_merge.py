def mpi_run(settings, nics, env, command, stdout=None, stderr=None):
    """
    Runs mpi_run.

    Args:
        settings: Settings for running MPI.
                  Note: settings.num_proc and settings.hosts must not be None.
        nics: Interfaces to include by MPI.
        env: Environment dictionary to use for running command.
        command: Command and arguments to run as a list of string.
        stdout: Stdout of the mpi process.
                Only used when settings.run_func_mode is True.
        stderr: Stderr of the mpi process.
                Only used when settings.run_func_mode is True.
    """
    if env is not None and not isinstance(env, dict):
        raise Exception('env argument must be a dict, not {type}: {env}'
                        .format(type=type(env), env=env))

    mpi_impl_flags, impl_binding_args = _get_mpi_implementation_flags(settings.tcp_flag, env=env)
    if mpi_impl_flags is None:
        raise Exception(_MPI_NOT_FOUND_ERROR_MSG)

    ssh_port_arg = '-mca plm_rsh_args \"-p {ssh_port}\"'.format(
            ssh_port=settings.ssh_port) if settings.ssh_port else ''

    # if user does not specify any hosts, mpirun by default uses local host.
    # There is no need to specify localhost.
    hosts_arg = '-H {hosts}'.format(hosts=settings.hosts)

    tcp_intf_arg = '-mca btl_tcp_if_include {nics}'.format(
        nics=','.join(nics)) if nics else ''
    nccl_socket_intf_arg = '-x NCCL_SOCKET_IFNAME={nics}'.format(
        nics=','.join(nics)) if nics else ''

    # On large cluster runs (e.g. Summit), we need extra settings to work around OpenMPI issues
    if settings.num_hosts and settings.num_hosts >= _LARGE_CLUSTER_THRESHOLD:
        mpi_impl_flags.append('-mca plm_rsh_no_tree_spawn true')
        mpi_impl_flags.append('-mca plm_rsh_num_concurrent {}'.format(settings.num_hosts))

    binding_args = settings.binding_args if settings.binding_args else ' '.join(impl_binding_args)

    # Pass all the env variables to the mpirun command.
    mpirun_command = (
        'mpirun --allow-run-as-root --tag-output '
        '-np {num_proc} {hosts_arg} '
        '{binding_args} '
        '{mpi_args} '
        '{ssh_port_arg} '
        '{tcp_intf_arg} '
        '{nccl_socket_intf_arg} '
        '{output_filename_arg} '
        '{env} {extra_mpi_args} {command}'  # expect a lot of environment variables
        .format(num_proc=settings.num_proc,
                hosts_arg=hosts_arg,
                binding_args=binding_args,
                mpi_args=' '.join(mpi_impl_flags),
                tcp_intf_arg=tcp_intf_arg,
                nccl_socket_intf_arg=nccl_socket_intf_arg,
                ssh_port_arg=ssh_port_arg,
                output_filename_arg='--output-filename ' + settings.output_filename
                                    if settings.output_filename else '',
                env=' '.join('-x %s' % key for key in sorted(env.keys())
                             if env_util.is_exportable(key)),

                extra_mpi_args=settings.extra_mpi_args if settings.extra_mpi_args else '',
                command=' '.join(quote(par) for par in command))
    )

    if settings.verbose >= 2:
        print(mpirun_command)

    # we need the driver's PATH in env to run mpirun,
    # env for mpirun is different to env encoded in mpirun_command
    if 'PATH' not in env and 'PATH' in os.environ:
        env = copy.copy(env)  # copy env so we do not leak env modifications
        env['PATH'] = os.environ['PATH']

    # Execute the mpirun command.
    if settings.run_func_mode:
        exit_code = safe_shell_exec.execute(mpirun_command, env=env, stdout=stdout, stderr=stderr)
        if exit_code != 0:
            raise RuntimeError("mpirun failed with exit code {exit_code}".format(exit_code=exit_code))
    else:
        os.execve('/bin/sh', ['/bin/sh', '-c', mpirun_command], env)
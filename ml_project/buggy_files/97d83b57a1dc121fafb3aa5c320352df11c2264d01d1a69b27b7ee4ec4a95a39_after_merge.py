def mpi_run(settings, nics, driver, env, stdout=None, stderr=None):
    """
    Runs mpirun.

    :param settings: Settings for running MPI.
                     Note: settings.num_proc and settings.hosts must not be None.
    :param nics: Interfaces to include by MPI.
    :param driver: The Spark driver service that tasks are connected to.
    :param env: Environment dictionary to use for running MPI.  Can be None.
    :param stdout: Stdout of the mpi process.
                   Only used when settings.run_func_mode is True.
    :param stderr: Stderr of the mpi process.
                   Only used when settings.run_func_mode is True.
    """
    env = {} if env is None else copy.copy(env)  # copy env so we do not leak env modifications

    # Pass secret key through the environment variables.
    env[secret.HOROVOD_SECRET_KEY] = codec.dumps_base64(settings.key)
    # we don't want the key to be serialized along with settings from here on
    settings.key = None

    rsh_agent = (sys.executable,
                 '-m', 'horovod.spark.driver.mpirun_rsh',
                 codec.dumps_base64(driver.addresses()),
                 codec.dumps_base64(settings))
    settings.extra_mpi_args = ('{extra_mpi_args} -x NCCL_DEBUG=INFO -mca plm_rsh_agent "{rsh_agent}"'
                               .format(extra_mpi_args=settings.extra_mpi_args if settings.extra_mpi_args else '',
                                       rsh_agent=' '.join(rsh_agent)))
    command = (sys.executable,
               '-m', 'horovod.spark.task.mpirun_exec_fn',
               codec.dumps_base64(driver.addresses()),
               codec.dumps_base64(settings))
    hr_mpi_run(settings, nics, env, command, stdout=stdout, stderr=stderr)
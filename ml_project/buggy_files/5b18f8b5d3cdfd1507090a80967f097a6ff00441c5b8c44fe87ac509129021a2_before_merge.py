def gloo_run(settings, nics, driver, env):
    """
    Run distributed gloo jobs.

    :param settings: Settings for running the distributed jobs.
                     Note: settings.num_proc and settings.hosts must not be None.
    :param nics: Interfaces to use by gloo.
    :param driver: The Spark driver service that tasks are connected to.
    :param env: Environment dictionary to use for running gloo jobs.  Can be None.
    """
    if env is None:
        env = {}

    # Each thread will use SparkTaskClient to launch the job on each remote host. If an
    # error occurs in one thread, entire process will be terminated. Otherwise,
    # threads will keep running and ssh session.
    iface = list(nics)[0]
    server_ip = driver.addresses()[iface][0][0]
    command = (sys.executable,
               '-m', 'horovod.spark.task.gloo_exec_fn',
               codec.dumps_base64(driver.addresses()),
               codec.dumps_base64(settings))

    exec_command = _exec_command_fn(driver.addresses(), settings.key, settings, env)
    launch_gloo(command, exec_command, settings, nics, {}, server_ip)
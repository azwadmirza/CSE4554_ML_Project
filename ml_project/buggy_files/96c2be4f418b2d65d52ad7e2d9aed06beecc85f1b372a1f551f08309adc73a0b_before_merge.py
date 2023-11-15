def run_experiment(stub_method_call=None,
                   batch_tasks=None,
                   exp_prefix="experiment",
                   exp_name=None,
                   log_dir=None,
                   script="scripts/run_experiment.py",
                   python_command="python",
                   mode="local",
                   dry=False,
                   docker_image=None,
                   aws_config=None,
                   env=None,
                   variant=None,
                   use_tf=False,
                   use_gpu=False,
                   sync_s3_pkl=False,
                   sync_s3_png=False,
                   sync_s3_log=False,
                   sync_log_on_termination=True,
                   confirm_remote=True,
                   terminate_machine=True,
                   periodic_sync=True,
                   periodic_sync_interval=15,
                   sync_all_data_node_to_s3=True,
                   use_cloudpickle=None,
                   pre_commands=None,
                   added_project_directories=[],
                   **kwargs):
    """
    Serialize the stubbed method call and run the experiment using the
    specified mode.
    :param stub_method_call: A stubbed method call.
    :param script: The name of the entrance point python script
    :param mode: Where and how to run the experiment. Should be one of "local",
     "local_docker", "ec2", or "lab_kube".
    :param dry: Whether to do a dry-run, which only prints the commands without
     executing them.
    :param exp_prefix: Name prefix for the experiments
    :param docker_image: name of the docker image. Ignored if using local mode.
    :param aws_config: configuration for AWS. Only used under EC2 mode
    :param env: extra environment variables
    :param kwargs: All other parameters will be passed directly to the entrance
     python script.
    :param variant: If provided, should be a dictionary of parameters
    :param use_tf: this flag is used along with the Theano and GPU
     configuration when using TensorFlow
    :param use_gpu: Whether the launched task is running on GPU. This triggers
     a few configuration changes including
    certain environment flags
    :param sync_s3_pkl: Whether to sync pkl files during execution of the
     experiment (they will always be synced at
    the end of the experiment)
    :param sync_s3_png: Whether to sync png files during execution of the
     experiment (they will always be synced at
    the end of the experiment)
    :param sync_s3_log: Whether to sync log files during execution of the
     experiment (they will always be synced at
    the end of the experiment)
    :param confirm_remote: Whether to confirm before launching experiments
     remotely
    :param terminate_machine: Whether to terminate machine after experiment
     finishes. Only used when using mode="ec2". This is useful when one wants
     to debug after an experiment finishes abnormally.
    :param periodic_sync: Whether to synchronize certain experiment files
     periodically during execution.
    :param periodic_sync_interval: Time interval between each periodic sync,
     in seconds.
    """
    assert stub_method_call is not None or batch_tasks is not None, \
        "Must provide at least either stub_method_call or batch_tasks"

    if use_cloudpickle is None:
        for maybe_stub in (batch_tasks or [stub_method_call]):
            # decide mode
            if isinstance(maybe_stub, StubBase):
                use_cloudpickle = False
            else:
                assert hasattr(maybe_stub, '__call__')
                use_cloudpickle = True
                # ensure variant exists
                if variant is None:
                    variant = dict()

    if batch_tasks is None:
        batch_tasks = [
            dict(
                kwargs,
                pre_commands=pre_commands,
                stub_method_call=stub_method_call,
                exp_name=exp_name,
                log_dir=log_dir,
                env=env,
                variant=variant,
                use_cloudpickle=use_cloudpickle)
        ]

    global exp_count
    global remote_confirmed
    config.USE_GPU = use_gpu
    config.USE_TF = use_tf

    if use_tf:
        if not use_gpu:
            os.environ['CUDA_VISIBLE_DEVICES'] = ""
        else:
            os.unsetenv('CUDA_VISIBLE_DEVICES')

    # params_list = []

    for task in batch_tasks:
        call = task.pop("stub_method_call")
        if use_cloudpickle:
            import cloudpickle
            data = base64.b64encode(cloudpickle.dumps(call)).decode("utf-8")
        else:
            data = base64.b64encode(pickle.dumps(call)).decode("utf-8")
        task["args_data"] = data
        exp_count += 1
        params = dict(kwargs)
        if task.get("exp_name", None) is None:
            task["exp_name"] = "%s_%s_%04d" % (exp_prefix, timestamp,
                                               exp_count)
        if task.get("log_dir", None) is None:
            task["log_dir"] = config.LOG_DIR + "/local/" + \
                              exp_prefix.replace("_", "-") + \
                              "/" + \
                              task["exp_name"]
        if task.get("variant", None) is not None:
            variant = task.pop("variant")
            if "exp_name" not in variant:
                variant["exp_name"] = task["exp_name"]
            task["variant_data"] = base64.b64encode(
                pickle.dumps(variant)).decode("utf-8")
        elif "variant" in task:
            del task["variant"]
        task["remote_log_dir"] = osp.join(config.AWS_S3_PATH,
                                          exp_prefix.replace("_", "-"),
                                          task["exp_name"])
        task["env"] = task.get("env", dict()) or dict()
        task["env"]["GARAGE_USE_GPU"] = str(use_gpu)
        task["env"]["GARAGE_USE_TF"] = str(use_tf)

    if mode not in ["local", "local_docker"
                    ] and not remote_confirmed and not dry and confirm_remote:
        remote_confirmed = query_yes_no(
            "Running in (non-dry) mode %s. Confirm?" % mode)
        if not remote_confirmed:
            sys.exit(1)

    if hasattr(mode, "__call__"):
        if docker_image is None:
            docker_image = config.DOCKER_IMAGE
        mode(
            task,
            docker_image=docker_image,
            use_gpu=use_gpu,
            exp_prefix=exp_prefix,
            script=script,
            python_command=python_command,
            sync_s3_pkl=sync_s3_pkl,
            sync_log_on_termination=sync_log_on_termination,
            periodic_sync=periodic_sync,
            periodic_sync_interval=periodic_sync_interval,
            sync_all_data_node_to_s3=sync_all_data_node_to_s3,
        )
    elif mode == "local":
        for task in batch_tasks:
            del task["remote_log_dir"]
            env = task.pop("env", None)
            command = to_local_command(
                task,
                python_command=python_command,
                script=osp.join(config.PROJECT_PATH, script),
                use_gpu=use_gpu)
            print(command)
            if dry:
                return
            try:
                if env is None:
                    env = dict()
                subprocess.call(
                    command, shell=True, env=dict(os.environ, **env))
            except Exception as e:
                print(e)
                if isinstance(e, KeyboardInterrupt):
                    raise
    elif mode == "local_docker":
        if docker_image is None:
            docker_image = config.DOCKER_IMAGE
        for task in batch_tasks:
            del task["remote_log_dir"]
            env = task.pop("env", None)
            command = to_docker_command(
                task,  # these are the params. Pre and Post command can be here
                docker_image=docker_image,
                script=script,
                env=env,
                use_gpu=use_gpu,
                use_tty=True,
                python_command=python_command,
            )
            print(command)
            if dry:
                return
            p = subprocess.Popen(command, shell=True)
            try:
                p.wait()
            except KeyboardInterrupt:
                try:
                    print("terminating")
                    p.terminate()
                except OSError:
                    print("os error!")
                    pass
                p.wait()
    elif mode == "ec2":
        if docker_image is None:
            docker_image = config.DOCKER_IMAGE
        s3_code_path = s3_sync_code(
            config,
            dry=dry,
            added_project_directories=added_project_directories)
        launch_ec2(
            batch_tasks,
            exp_prefix=exp_prefix,
            docker_image=docker_image,
            python_command=python_command,
            script=script,
            aws_config=aws_config,
            dry=dry,
            terminate_machine=terminate_machine,
            use_gpu=use_gpu,
            code_full_path=s3_code_path,
            sync_s3_pkl=sync_s3_pkl,
            sync_s3_png=sync_s3_png,
            sync_s3_log=sync_s3_log,
            sync_log_on_termination=sync_log_on_termination,
            periodic_sync=periodic_sync,
            periodic_sync_interval=periodic_sync_interval)
    elif mode == "lab_kube":
        # assert env is None
        # first send code folder to s3
        s3_code_path = s3_sync_code(config, dry=dry)
        if docker_image is None:
            docker_image = config.DOCKER_IMAGE
        for task in batch_tasks:
            # if 'env' in task:
            #     assert task.pop('env') is None
            # TODO: dangerous when there are multiple tasks?
            task["resources"] = params.pop("resources",
                                           config.KUBE_DEFAULT_RESOURCES)
            task["node_selector"] = params.pop(
                "node_selector", config.KUBE_DEFAULT_NODE_SELECTOR)
            task["exp_prefix"] = exp_prefix
            pod_dict = to_lab_kube_pod(
                task,
                code_full_path=s3_code_path,
                docker_image=docker_image,
                script=script,
                is_gpu=use_gpu,
                python_command=python_command,
                sync_s3_pkl=sync_s3_pkl,
                periodic_sync=periodic_sync,
                periodic_sync_interval=periodic_sync_interval,
                sync_all_data_node_to_s3=sync_all_data_node_to_s3,
                terminate_machine=terminate_machine,
            )
            pod_str = json.dumps(pod_dict, indent=1)
            if dry:
                print(pod_str)
            dir = "{pod_dir}/{exp_prefix}".format(
                pod_dir=config.POD_DIR, exp_prefix=exp_prefix)
            ensure_dir(dir)
            fname = "{dir}/{exp_name}.json".format(
                dir=dir, exp_name=task["exp_name"])
            with open(fname, "w") as fh:
                fh.write(pod_str)
            kubecmd = "kubectl create -f %s" % fname
            print(kubecmd)
            if dry:
                return
            retry_count = 0
            wait_interval = 1
            while retry_count <= 5:
                try:
                    return_code = subprocess.call(kubecmd, shell=True)
                    if return_code == 0:
                        break
                    retry_count += 1
                    print("trying again...")
                    time.sleep(wait_interval)
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        raise
                    print(e)
    else:
        raise NotImplementedError
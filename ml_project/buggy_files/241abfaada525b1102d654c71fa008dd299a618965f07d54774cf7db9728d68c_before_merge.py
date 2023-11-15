def run_docker_command(
    runner: Runner,
    remote_info: RemoteInfo,
    args: argparse.Namespace,
    remote_env: Dict[str, str],
    subprocesses: Subprocesses,
    ssh: SSH,
    mount_dir: Optional[str],
) -> Popen:
    """
    --docker-run support.

    Connect using sshuttle running in a Docker container, and then run user
    container.

    :param args: Command-line args to telepresence binary.
    :param remote_env: Dictionary with environment on remote pod.
    :param mount_dir: Path to local directory where remote pod's filesystem is
        mounted.
    """
    # Update environment:
    if mount_dir:
        remote_env["TELEPRESENCE_ROOT"] = mount_dir
    remote_env["TELEPRESENCE_METHOD"] = "container"  # mostly just for tests :(

    # Extract --publish flags and add them to the sshuttle container, which is
    # responsible for defining the network entirely.
    docker_args, publish_args = parse_docker_args(args.docker_run)

    # Start the sshuttle container:
    name = random_name()
    config = {
        "port":
        ssh.port,
        "cidrs":
        get_proxy_cidrs(
            runner, args, remote_info, remote_env["KUBERNETES_SERVICE_HOST"]
        ),
        "expose_ports":
        list(args.expose.local_to_remote()),
    }
    if sys.platform == "darwin":
        config["ip"] = MAC_LOOPBACK_IP
    # Image already has tini init so doesn't need --init option:
    span = runner.span()
    subprocesses.append(
        runner.popen(
            docker_runify(
                publish_args + [
                    "--rm", "--privileged", "--name=" + name,
                    TELEPRESENCE_LOCAL_IMAGE, "proxy",
                    json.dumps(config)
                ]
            )
        ), make_docker_kill(runner, name)
    )

    # Write out env file:
    with NamedTemporaryFile("w", delete=False) as envfile:
        for key, value in remote_env.items():
            envfile.write("{}={}\n".format(key, value))
    atexit.register(os.remove, envfile.name)

    # Wait for sshuttle to be running:
    while True:
        try:
            runner.check_call(
                docker_runify([
                    "--network=container:" + name, "--rm",
                    TELEPRESENCE_LOCAL_IMAGE, "wait"
                ])
            )
        except CalledProcessError as e:
            if e.returncode == 100:
                # We're good!
                break
            elif e.returncode == 125:
                # Docker failure, probably due to original container not
                # starting yet... so sleep and try again:
                sleep(1)
                continue
            else:
                raise
        else:
            raise RuntimeError(
                "Waiting container exited prematurely. File a bug, please!"
            )

    # Start the container specified by the user:
    container_name = random_name()
    docker_command = docker_runify([
        "--name=" + container_name,
        "--network=container:" + name,
        "--env-file=" + envfile.name,
    ])
    if mount_dir:
        docker_command.append("--volume={}:{}".format(mount_dir, mount_dir))
    # Don't add --init if the user is doing something with it
    init_args = [
        arg for arg in docker_args
        if arg == "--init" or arg.startswith("--init=")
    ]
    # Older versions of Docker don't have --init:
    if not init_args and "--init" in runner.get_output([
        "docker", "run", "--help"
    ]):
        docker_command += ["--init"]
    docker_command += docker_args
    span.end()
    p = Popen(docker_command)

    def terminate_if_alive():
        runner.write("Shutting down containers...\n")
        if p.poll() is None:
            runner.write("Killing local container...\n")
            make_docker_kill(runner, container_name)()

    atexit.register(terminate_if_alive)
    return p
def docker_start_cmds(user, image, mount, cname, user_options):
    cmds = []

    # create flags
    # ports for the redis, object manager, and tune client
    port_flags = " ".join([
        "-p {port}:{port}".format(port=port)
        for port in ["6379", "8076", "4321"]
    ])
    mount_flags = " ".join(
        ["-v {src}:{dest}".format(src=k, dest=v) for k, v in mount.items()])

    # for click, used in ray cli
    env_vars = {"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"}
    env_flags = " ".join(
        ["-e {name}={val}".format(name=k, val=v) for k, v in env_vars.items()])

    user_options_str = " ".join(user_options)
    # docker run command
    docker_check = [
        "docker", "inspect", "-f", "'{{.State.Running}}'", cname, "||"
    ]
    docker_run = [
        "docker", "run", "--rm", "--name {}".format(cname), "-d", "-it",
        port_flags, mount_flags, env_flags, user_options_str, "--net=host",
        image, "bash"
    ]
    cmds.append(" ".join(docker_check + docker_run))

    return cmds
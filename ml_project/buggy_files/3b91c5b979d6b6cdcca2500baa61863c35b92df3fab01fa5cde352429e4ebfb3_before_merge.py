def ray_new_dir(yaml_path: str, new_dir: str, docker: bool) -> None:
    """
    The output of exec os.getcwd() via ray on remote cluster.
    """
    args = ["ray", "exec"]
    if docker:
        args += "--docker"

    mktemp_args = args + [yaml_path, f"mkdir -p {new_dir}"]
    _run_command(mktemp_args)
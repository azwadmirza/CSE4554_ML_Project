def ray_new_dir(yaml_path: str, new_dir: str, run_env: str) -> None:
    """
    The output of exec os.getcwd() via ray on remote cluster.
    """
    args = ["ray", "exec", f"--run-env={run_env}"]
    mktemp_args = args + [yaml_path, f"mkdir -p {new_dir}"]
    _run_command(mktemp_args)
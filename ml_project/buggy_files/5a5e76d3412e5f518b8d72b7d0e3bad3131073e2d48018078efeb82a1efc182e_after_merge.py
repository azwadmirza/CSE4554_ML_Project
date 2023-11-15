def ray_up(yaml_path: str) -> None:
    args = ["ray", "up", "-y", yaml_path]
    _run_command(args)
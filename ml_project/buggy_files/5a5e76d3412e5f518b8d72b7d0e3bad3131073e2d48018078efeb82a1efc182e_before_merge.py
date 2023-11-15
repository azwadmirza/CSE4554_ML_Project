def ray_up(yaml_path: str) -> None:
    _run_command(["ray", "up", "-y", yaml_path])
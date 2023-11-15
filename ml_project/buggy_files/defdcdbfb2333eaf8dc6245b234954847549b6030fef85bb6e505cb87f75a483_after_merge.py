def ray_exec(yaml_path: str, run_env: str, file_path: str, pickle_path: str) -> None:
    command = f"python {file_path} {pickle_path}"
    args = ["ray", "exec", f"--run-env={run_env}"]
    args += [yaml_path, command]
    _run_command(args)
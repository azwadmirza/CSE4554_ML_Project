def ray_exec(yaml_path: str, docker: bool, file_path: str, pickle_path: str) -> None:
    command = f"python {file_path} {pickle_path}"
    args = ["ray", "exec"]
    if docker:
        args.append("--docker")
    args += [yaml_path, command]
    _run_command(args)
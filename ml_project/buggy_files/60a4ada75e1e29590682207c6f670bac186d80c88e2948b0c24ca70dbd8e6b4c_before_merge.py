def ray_tmp_dir(yaml_path: str, docker: bool) -> Generator[Any, None, None]:
    args = ["ray", "exec"]
    if docker:
        args.append("--docker")

    mktemp_args = args + [yaml_path, "echo $(mktemp -d)"]
    out, _ = _run_command(mktemp_args)
    tmppath = [
        x
        for x in out.strip().split()
        if x.startswith("/tmp/") and "ray-config" not in x  # nosec
    ]
    assert len(tmppath) == 1, f"tmppath is : {tmppath}"
    tmp_path = tmppath[0]
    log.info(f"Created temp path on remote server {tmp_path}")
    yield tmp_path
    rmtemp_args = args + [yaml_path, f"rm -rf {tmp_path}"]
    _run_command(rmtemp_args)
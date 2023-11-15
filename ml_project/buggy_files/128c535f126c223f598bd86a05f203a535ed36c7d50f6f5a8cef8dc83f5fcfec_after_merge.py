def cmd_output_b(
        *cmd: str,
        retcode: Optional[int] = 0,
        **kwargs: Any,
) -> Tuple[int, bytes, Optional[bytes]]:
    _setdefault_kwargs(kwargs)

    try:
        cmd = parse_shebang.normalize_cmd(cmd)
    except parse_shebang.ExecutableNotFoundError as e:
        returncode, stdout_b, stderr_b = e.to_output()
    else:
        try:
            proc = subprocess.Popen(cmd, **kwargs)
        except OSError as e:
            returncode, stdout_b, stderr_b = _oserror_to_output(e)
        else:
            stdout_b, stderr_b = proc.communicate()
            returncode = proc.returncode

    if retcode is not None and retcode != returncode:
        raise CalledProcessError(returncode, cmd, retcode, stdout_b, stderr_b)

    return returncode, stdout_b, stderr_b
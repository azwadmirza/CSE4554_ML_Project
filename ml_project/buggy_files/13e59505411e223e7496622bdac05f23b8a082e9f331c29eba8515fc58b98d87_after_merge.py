def xargs(cmd, varargs, **kwargs):
    """A simplified implementation of xargs.

    negate: Make nonzero successful and zero a failure
    target_concurrency: Target number of partitions to run concurrently
    """
    negate = kwargs.pop('negate', False)
    target_concurrency = kwargs.pop('target_concurrency', 1)
    max_length = kwargs.pop('_max_length', _get_platform_max_length())
    retcode = 0
    stdout = b''
    stderr = b''

    try:
        cmd = parse_shebang.normalize_cmd(cmd)
    except parse_shebang.ExecutableNotFoundError as e:
        return e.to_output()

    partitions = partition(cmd, varargs, target_concurrency, max_length)

    def run_cmd_partition(run_cmd):
        return cmd_output(*run_cmd, encoding=None, retcode=None, **kwargs)

    threads = min(len(partitions), target_concurrency)
    with _thread_mapper(threads) as thread_map:
        results = thread_map(run_cmd_partition, partitions)

        for proc_retcode, proc_out, proc_err in results:
            # This is *slightly* too clever so I'll explain it.
            # First the xor boolean table:
            #     T | F |
            #   +-------+
            # T | F | T |
            # --+-------+
            # F | T | F |
            # --+-------+
            # When negate is True, it has the effect of flipping the return
            # code. Otherwise, the returncode is unchanged.
            retcode |= bool(proc_retcode) ^ negate
            stdout += proc_out
            stderr += proc_err

    return retcode, stdout, stderr
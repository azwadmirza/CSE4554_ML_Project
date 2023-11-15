def run_cmd(cwd, cmd, env=None):
    logger.debug('Executing "{}"'.format(' '.join(cmd)))
    if len(cmd) == 0:
        raise dbt.exceptions.CommandError(cwd, cmd)

    # the env argument replaces the environment entirely, which has exciting
    # consequences on Windows! Do an update instead.
    full_env = env
    if env is not None:
        full_env = os.environ.copy()
        full_env.update(env)

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env)

        out, err = proc.communicate()
    except OSError as exc:
        _interpret_oserror(exc, cwd, cmd)

    logger.debug('STDOUT: "{}"'.format(out))
    logger.debug('STDERR: "{}"'.format(err))

    if proc.returncode != 0:
        logger.debug('command return code={}'.format(proc.returncode))
        raise dbt.exceptions.CommandResultError(cwd, cmd, proc.returncode,
                                                out, err)

    return out, err
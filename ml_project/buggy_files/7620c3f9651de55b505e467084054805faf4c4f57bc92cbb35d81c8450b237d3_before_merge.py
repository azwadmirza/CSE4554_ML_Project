def run_hook(repo_cmd_runner, hook, file_args):
    return repo_cmd_runner.run(
        ['xargs', '-0'] + shlex.split(hook['entry']) + hook['args'],
        stdin=file_args_to_stdin(file_args),
        retcode=None,
    )
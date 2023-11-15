def run_hook(repo_cmd_runner, hook, file_args):
    return repo_cmd_runner.run(
        ['xargs', '-0', '{{prefix}}{0}'.format(hook['entry'])] + hook['args'],
        # TODO: this is duplicated in pre_commit/languages/helpers.py
        stdin=file_args_to_stdin(file_args),
        retcode=None,
    )
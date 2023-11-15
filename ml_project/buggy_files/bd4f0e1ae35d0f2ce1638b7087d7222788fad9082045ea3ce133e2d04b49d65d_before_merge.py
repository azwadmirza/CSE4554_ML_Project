def run_hook(repo_cmd_runner, hook, file_args):
    # For PCRE the entry is the regular expression to match
    return repo_cmd_runner.run(
        [
            'xargs', '-0', 'sh', '-c',
            # Grep usually returns 0 for matches, and nonzero for non-matches
            # so we flip it here.
            '! grep -H -n -P {0} $@'.format(shell_escape(hook['entry'])),
            '--',
        ],
        stdin=file_args_to_stdin(file_args),
        retcode=None,
    )
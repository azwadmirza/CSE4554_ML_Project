def run_hook(env, hook, file_args):
    quoted_args = [pipes.quote(arg) for arg in hook['args']]
    return env.run(
        # Use -s 4000 (slightly less than posix mandated minimum)
        # This is to prevent "xargs: ... Bad file number" on windows
        ' '.join(['xargs', '-0', '-s4000', hook['entry']] + quoted_args),
        stdin=file_args_to_stdin(file_args),
        retcode=None,
    )
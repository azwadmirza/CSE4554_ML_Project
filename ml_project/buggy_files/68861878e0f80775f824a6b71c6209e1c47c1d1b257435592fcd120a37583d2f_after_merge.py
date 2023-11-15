def do_run(cmd, asynchronous, print_output=None, env_vars={}):
    sys.stdout.flush()
    if asynchronous:
        if is_debug() and print_output is None:
            print_output = True
        outfile = subprocess.PIPE if print_output else None
        t = ShellCommandThread(cmd, outfile=outfile, env_vars=env_vars)
        t.start()
        TMP_THREADS.append(t)
        return t
    return run(cmd, env_vars=env_vars)
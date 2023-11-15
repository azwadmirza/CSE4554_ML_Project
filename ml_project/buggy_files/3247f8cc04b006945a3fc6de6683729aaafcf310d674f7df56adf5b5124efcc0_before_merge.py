def _exec_middleman(command, env, exit_event, stdout, stderr, rw):
    stdout_r, stdout_w = stdout
    stderr_r, stderr_w = stderr
    r, w = rw

    # Close unused file descriptors to enforce PIPE behavior.
    stdout_r.close()
    stderr_r.close()
    w.close()
    os.setsid()

    executor_shell = subprocess.Popen(command, shell=True, env=env,
                                      stdout=stdout_w, stderr=stderr_w)

    # we don't bother stopping the on_event thread, this process sys.exits soon
    # so the on_event thread has to be a deamon thread
    on_event(exit_event, terminate_executor_shell_and_children, args=(executor_shell.pid,), daemon=True)

    def kill_executor_children_if_parent_dies():
        # This read blocks until the pipe is closed on the other side
        # due to parent process termination (for any reason, including -9).
        os.read(r.fileno(), 1)
        terminate_executor_shell_and_children(executor_shell.pid)

    in_thread(kill_executor_children_if_parent_dies)

    exit_code = executor_shell.wait()
    if exit_code < 0:
        # See: https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html
        exit_code = 128 + abs(exit_code)

    sys.exit(exit_code)
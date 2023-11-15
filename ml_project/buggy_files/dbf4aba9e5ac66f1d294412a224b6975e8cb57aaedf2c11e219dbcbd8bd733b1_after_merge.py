def run_pexpect(args, cwd, env, logfile,
                cancelled_callback=None, expect_passwords={},
                extra_update_fields=None, idle_timeout=None, job_timeout=0,
                pexpect_timeout=5, proot_cmd='bwrap'):
    '''
    Run the given command using pexpect to capture output and provide
    passwords when requested.

    :param args:                a list of `subprocess.call`-style arguments
                                representing a subprocess e.g., ['ls', '-la']
    :param cwd:                 the directory in which the subprocess should
                                run
    :param env:                 a dict containing environment variables for the
                                subprocess, ala `os.environ`
    :param logfile:             a file-like object for capturing stdout
    :param cancelled_callback:  a callable - which returns `True` or `False`
                                - signifying if the job has been prematurely
                                  cancelled
    :param expect_passwords:    a dict of regular expression password prompts
                                to input values, i.e., {r'Password:\s*?$':
                                'some_password'}
    :param extra_update_fields: a dict used to specify DB fields which should
                                be updated on the underlying model
                                object after execution completes
    :param idle_timeout         a timeout (in seconds); if new output is not
                                sent to stdout in this interval, the process
                                will be terminated
    :param job_timeout          a timeout (in seconds); if the total job runtime
                                exceeds this, the process will be killed
    :param pexpect_timeout      a timeout (in seconds) to wait on
                                `pexpect.spawn().expect()` calls
    :param proot_cmd            the command used to isolate processes, `bwrap`

    Returns a tuple (status, return_code) i.e., `('successful', 0)`
    '''
    expect_passwords[pexpect.TIMEOUT] = None
    expect_passwords[pexpect.EOF] = None

    if not isinstance(expect_passwords, collections.OrderedDict):
        # We iterate over `expect_passwords.keys()` and
        # `expect_passwords.values()` separately to map matched inputs to
        # patterns and choose the proper string to send to the subprocess;
        # enforce usage of an OrderedDict so that the ordering of elements in
        # `keys()` matches `values()`.
        expect_passwords = collections.OrderedDict(expect_passwords)
    password_patterns = expect_passwords.keys()
    password_values = expect_passwords.values()

    child = pexpect.spawn(
        args[0], args[1:], cwd=cwd, env=env, ignore_sighup=True,
        encoding='utf-8', echo=False, use_poll=True
    )
    child.logfile_read = logfile
    canceled = False
    timed_out = False
    errored = False
    last_stdout_update = time.time()

    job_start = time.time()
    while child.isalive():
        result_id = child.expect(password_patterns, timeout=pexpect_timeout, searchwindowsize=100)
        password = password_values[result_id]
        if password is not None:
            child.sendline(password)
            last_stdout_update = time.time()
        if cancelled_callback:
            try:
                canceled = cancelled_callback()
            except Exception:
                logger.exception('Could not check cancel callback - canceling immediately')
                if isinstance(extra_update_fields, dict):
                    extra_update_fields['job_explanation'] = "System error during job execution, check system logs"
                errored = True
        else:
            canceled = False
        if not canceled and job_timeout != 0 and (time.time() - job_start) > job_timeout:
            timed_out = True
            if isinstance(extra_update_fields, dict):
                extra_update_fields['job_explanation'] = "Job terminated due to timeout"
        if canceled or timed_out or errored:
            handle_termination(child.pid, child.args, proot_cmd, is_cancel=canceled)
        if idle_timeout and (time.time() - last_stdout_update) > idle_timeout:
            child.close(True)
            canceled = True
    if errored:
        return 'error', child.exitstatus
    elif canceled:
        return 'canceled', child.exitstatus
    elif child.exitstatus == 0 and not timed_out:
        return 'successful', child.exitstatus
    else:
        return 'failed', child.exitstatus
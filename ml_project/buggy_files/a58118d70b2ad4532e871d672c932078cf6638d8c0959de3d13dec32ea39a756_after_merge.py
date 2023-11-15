def _run_code_snippet(caller, pycode, mode="eval", measure_time=False,
                      client_raw=False, show_input=True):
    """
    Run code and try to display information to the caller.

    Args:
        caller (Object): The caller.
        pycode (str): The Python code to run.
        measure_time (bool, optional): Should we measure the time of execution?
        client_raw (bool, optional): Should we turn off all client-specific escaping?
        show_input (bookl, optional): Should we display the input?

    """
    # Try to retrieve the session
    session = caller
    if hasattr(caller, "sessions"):
        sessions = caller.sessions.all()

    available_vars = evennia_local_vars(caller)

    if show_input:
        for session in sessions:
            try:
                caller.msg(">>> %s" % pycode, session=session,
                           options={"raw": True})
            except TypeError:
                caller.msg(">>> %s" % pycode, options={"raw": True})




    try:
        # reroute standard output to game client console
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        class FakeStd:
            def __init__(self, caller):
                self.caller = caller

            def write(self, string):
                self.caller.msg(string.rsplit("\n", 1)[0])

        fake_std = FakeStd(caller)
        sys.stdout = fake_std
        sys.stderr = fake_std

        try:
            pycode_compiled = compile(pycode, "", mode)
        except Exception:
            mode = "exec"
            pycode_compiled = compile(pycode, "", mode)

        duration = ""
        if measure_time:
            t0 = time.time()
            ret = eval(pycode_compiled, {}, available_vars)
            t1 = time.time()
            duration = " (runtime ~ %.4f ms)" % ((t1 - t0) * 1000)
            caller.msg(duration)
        else:
            ret = eval(pycode_compiled, {}, available_vars)

    except Exception:
        errlist = traceback.format_exc().split('\n')
        if len(errlist) > 4:
            errlist = errlist[4:]
        ret = "\n".join("%s" % line for line in errlist if line)
    finally:
        # return to old stdout
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    if ret is None:
        return

    for session in sessions:
        try:
            caller.msg(ret, session=session, options={"raw": True,
                                                      "client_raw": client_raw})
        except TypeError:
            caller.msg(ret, options={"raw": True,
                                     "client_raw": client_raw})
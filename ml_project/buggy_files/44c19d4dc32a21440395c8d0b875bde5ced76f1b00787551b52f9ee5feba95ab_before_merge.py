def run_subproc(cmds, captured=False):
    """Runs a subprocess, in its many forms. This takes a list of 'commands,'
    which may be a list of command line arguments or a string, representing
    a special connecting character.  For example::

        $ ls | grep wakka

    is represented by the following cmds::

        [['ls'], '|', ['grep', 'wakka']]

    Lastly, the captured argument affects only the last real command.
    """
    specs = cmds_to_specs(cmds, captured=captured)
    captured = specs[-1].captured
    procs = []
    proc = pipeline_group = None
    for spec in specs:
        starttime = time.time()
        proc = spec.run(pipeline_group=pipeline_group)
        procs.append(proc)
        if ON_POSIX and pipeline_group is None and \
           spec.cls is subprocess.Popen:
            pipeline_group = proc.pid
    if not spec.is_proxy:
        add_job({
            'cmds': cmds,
            'pids': [i.pid for i in procs],
            'obj': proc,
            'bg': spec.background,
        })
    if _should_set_title(captured=captured):
        # set title here to get currently executing command
        pause_call_resume(proc, builtins.__xonsh_shell__.settitle)
    # create command or return if backgrounding.
    if spec.background:
        return
    if captured == 'hiddenobject':
        command = HiddenCommandPipeline(specs, procs, starttime=starttime,
                                        captured=captured)
    else:
        command = CommandPipeline(specs, procs, starttime=starttime,
                                  captured=captured)
    # now figure out what we should return.
    if captured == 'stdout':
        command.end()
        return command.output
    elif captured == 'object':
        return command
    elif captured == 'hiddenobject':
        command.end()
        return command
    else:
        command.end()
        return
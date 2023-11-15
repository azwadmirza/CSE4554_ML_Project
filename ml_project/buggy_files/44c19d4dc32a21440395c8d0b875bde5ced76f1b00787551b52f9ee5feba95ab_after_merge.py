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
    if captured == 'hiddenobject':
        command = HiddenCommandPipeline(specs)
    else:
        command = CommandPipeline(specs)
    proc = command.proc
    background = command.spec.background
    if not all(x.is_proxy for x in specs):
        add_job({
            'cmds': cmds,
            'pids': [i.pid for i in command.procs],
            'obj': proc,
            'bg': background,
            'pipeline': command,
            'pgrp': command.term_pgid,
        })
    if _should_set_title(captured=captured):
        # set title here to get currently executing command
        pause_call_resume(proc, builtins.__xonsh_shell__.settitle)
    # create command or return if backgrounding.
    if background:
        return
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
def _run_nodejs(script, input):
    if _nodejs is None:
        raise RuntimeError('node.js is needed to allow compilation of custom models ' +
                           '("conda install -c bokeh nodejs" or follow https://nodejs.org/en/download/)')

    proc = Popen([_nodejs, script], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    (stdout, errout) = proc.communicate(input=json.dumps(input).encode())

    if proc.returncode != 0:
        raise RuntimeError(errout)
    else:
        return AttrDict(json.loads(stdout.decode()))
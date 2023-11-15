def _run_npm(argv):
    if _nodejs is None:
        raise RuntimeError('node.js is needed to allow compilation of custom models ' +
                           '("conda install -c bokeh nodejs" or follow https://nodejs.org/en/download/)')

    _npm = join(dirname(_nodejs), "npm")
    proc = Popen([_npm] + argv, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    (_stdout, errout) = proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(errout)
    else:
        return None
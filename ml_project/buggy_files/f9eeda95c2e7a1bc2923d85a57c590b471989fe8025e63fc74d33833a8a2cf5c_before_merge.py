def maybe_reexec_pex(compatibility_constraints):
  """
  Handle environment overrides for the Python interpreter to use when executing this pex.

  This function supports interpreter filtering based on interpreter constraints stored in PEX-INFO
  metadata. If PEX_PYTHON is set in a pexrc, it attempts to obtain the binary location of the
  interpreter specified by PEX_PYTHON. If PEX_PYTHON_PATH is set, it attempts to search the path for
  a matching interpreter in accordance with the interpreter constraints. If both variables are
  present in a pexrc, this function gives precedence to PEX_PYTHON_PATH and errors out if no
  compatible interpreters can be found on said path. If neither variable is set, fall through to
  plain pex execution using PATH searching or the currently executing interpreter.

  :param compatibility_constraints: list of requirements-style strings that constrain the
  Python interpreter to re-exec this pex with.

  """
  if ENV.SHOULD_EXIT_BOOTSTRAP_REEXEC:
    return

  selected_interpreter = None
  with TRACER.timed('Selecting runtime interpreter based on pexrc', V=3):
    if ENV.PEX_PYTHON and not ENV.PEX_PYTHON_PATH:
      # preserve PEX_PYTHON re-exec for backwards compatibility
      # TODO: Kill this off completely in favor of PEX_PYTHON_PATH
      # https://github.com/pantsbuild/pex/issues/431
      selected_interpreter = _select_pex_python_interpreter(ENV.PEX_PYTHON,
                                                            compatibility_constraints)
    elif ENV.PEX_PYTHON_PATH:
      selected_interpreter = _select_interpreter(ENV.PEX_PYTHON_PATH, compatibility_constraints)

  if selected_interpreter:
    ENV.delete('PEX_PYTHON')
    ENV.delete('PEX_PYTHON_PATH')
    ENV.SHOULD_EXIT_BOOTSTRAP_REEXEC = True
    cmdline = [selected_interpreter] + sys.argv[1:]
    TRACER.log('Re-executing: cmdline="%s", sys.executable="%s", PEX_PYTHON="%s", '
               'PEX_PYTHON_PATH="%s", COMPATIBILITY_CONSTRAINTS="%s"'
               % (cmdline, sys.executable, ENV.PEX_PYTHON, ENV.PEX_PYTHON_PATH,
                  compatibility_constraints))
    os.execve(selected_interpreter, cmdline, ENV.copy())
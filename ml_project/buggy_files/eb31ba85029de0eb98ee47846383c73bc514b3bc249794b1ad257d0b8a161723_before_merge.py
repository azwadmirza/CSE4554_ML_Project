def maybe_reexec_pex(compatibility_constraints=None):
    # type: (Optional[Iterable[str]]) -> Union[None, NoReturn]
    """Handle environment overrides for the Python interpreter to use when executing this pex.

    This function supports interpreter filtering based on interpreter constraints stored in PEX-INFO
    metadata. If PEX_PYTHON is set it attempts to obtain the binary location of the interpreter
    specified by PEX_PYTHON. If PEX_PYTHON_PATH is set, it attempts to search the path for a matching
    interpreter in accordance with the interpreter constraints. If both variables are present, this
    function gives precedence to PEX_PYTHON_PATH and errors out if no compatible interpreters can be
    found on said path.

    If neither variable is set, we fall back to plain PEX execution using PATH searching or the
    currently executing interpreter. If compatibility constraints are used, we match those constraints
    against these interpreters.

    :param compatibility_constraints: optional list of requirements-style strings that constrain the
                                      Python interpreter to re-exec this pex with.
    """

    current_interpreter = PythonInterpreter.get()
    target = None  # type: Optional[PythonInterpreter]

    # NB: Used only for tests.
    if "_PEX_EXEC_CHAIN" in os.environ:
        flag_or_chain = os.environ.pop("_PEX_EXEC_CHAIN")
        pex_exec_chain = [] if flag_or_chain == "1" else flag_or_chain.split(os.pathsep)
        pex_exec_chain.append(current_interpreter.binary)
        os.environ["_PEX_EXEC_CHAIN"] = os.pathsep.join(pex_exec_chain)

    current_interpreter_blessed_env_var = "_PEX_SHOULD_EXIT_BOOTSTRAP_REEXEC"
    if os.environ.pop(current_interpreter_blessed_env_var, None):
        # We've already been here and selected an interpreter. Continue to execution.
        return None

    from . import pex

    pythonpath = pex.PEX.stash_pythonpath()
    if pythonpath is not None:
        TRACER.log("Stashed PYTHONPATH of {}".format(pythonpath), V=2)

    with TRACER.timed("Selecting runtime interpreter", V=3):
        if ENV.PEX_PYTHON and not ENV.PEX_PYTHON_PATH:
            # preserve PEX_PYTHON re-exec for backwards compatibility
            # TODO: Kill this off completely in favor of PEX_PYTHON_PATH
            # https://github.com/pantsbuild/pex/issues/431
            TRACER.log(
                "Using PEX_PYTHON={} constrained by {}".format(
                    ENV.PEX_PYTHON, compatibility_constraints
                ),
                V=3,
            )
            try:
                if os.path.isabs(ENV.PEX_PYTHON):
                    target = _select_path_interpreter(
                        path=ENV.PEX_PYTHON,
                        compatibility_constraints=compatibility_constraints,
                    )
                else:
                    target = _select_path_interpreter(
                        valid_basenames=(os.path.basename(ENV.PEX_PYTHON),),
                        compatibility_constraints=compatibility_constraints,
                    )
            except UnsatisfiableInterpreterConstraintsError as e:
                die(
                    e.create_message(
                        "Failed to find a compatible PEX_PYTHON={pex_python}.".format(
                            pex_python=ENV.PEX_PYTHON
                        )
                    )
                )
        elif ENV.PEX_PYTHON_PATH or compatibility_constraints:
            TRACER.log(
                "Using {path} constrained by {constraints}".format(
                    path="PEX_PYTHON_PATH={}".format(ENV.PEX_PYTHON_PATH)
                    if ENV.PEX_PYTHON_PATH
                    else "$PATH",
                    constraints=compatibility_constraints,
                ),
                V=3,
            )
            try:
                target = _select_path_interpreter(
                    path=ENV.PEX_PYTHON_PATH, compatibility_constraints=compatibility_constraints
                )
            except UnsatisfiableInterpreterConstraintsError as e:
                die(
                    e.create_message(
                        "Failed to find compatible interpreter on path {path}.".format(
                            path=ENV.PEX_PYTHON_PATH or os.getenv("PATH")
                        )
                    )
                )
        elif pythonpath is None:
            TRACER.log(
                "Using the current interpreter {} since no constraints have been specified and "
                "PYTHONPATH is not set.".format(sys.executable),
                V=3,
            )
            return None
        else:
            target = current_interpreter

    if not target:
        # N.B.: This can only happen when PEX_PYTHON_PATH is set and compatibility_constraints is
        # not set, but we handle all constraints generally for sanity sake.
        constraints = []
        if ENV.PEX_PYTHON:
            constraints.append("PEX_PYTHON={}".format(ENV.PEX_PYTHON))
        if ENV.PEX_PYTHON_PATH:
            constraints.append("PEX_PYTHON_PATH={}".format(ENV.PEX_PYTHON_PATH))
        if compatibility_constraints:
            constraints.extend(
                "--interpreter-constraint={}".format(compatibility_constraint)
                for compatibility_constraint in compatibility_constraints
            )

        die(
            "Failed to find an appropriate Python interpreter.\n"
            "\n"
            "Although the current interpreter is {python}, the following constraints exclude it:\n"
            "  {constraints}".format(python=sys.executable, constraints="\n  ".join(constraints))
        )

    os.environ.pop("PEX_PYTHON", None)
    os.environ.pop("PEX_PYTHON_PATH", None)

    if pythonpath is None and target == current_interpreter:
        TRACER.log(
            "Using the current interpreter {} since it matches constraints and "
            "PYTHONPATH is not set.".format(sys.executable)
        )
        return None

    target_binary = target.binary
    cmdline = [target_binary] + sys.argv
    TRACER.log(
        "Re-executing: "
        "cmdline={cmdline!r}, "
        "sys.executable={python!r}, "
        "PEX_PYTHON={pex_python!r}, "
        "PEX_PYTHON_PATH={pex_python_path!r}, "
        "COMPATIBILITY_CONSTRAINTS={compatibility_constraints!r}"
        "{pythonpath}".format(
            cmdline=" ".join(cmdline),
            python=sys.executable,
            pex_python=ENV.PEX_PYTHON,
            pex_python_path=ENV.PEX_PYTHON_PATH,
            compatibility_constraints=compatibility_constraints,
            pythonpath=', (stashed) PYTHONPATH="{}"'.format(pythonpath)
            if pythonpath is not None
            else "",
        )
    )

    # Avoid a re-run through compatibility_constraint checking.
    os.environ[current_interpreter_blessed_env_var] = "1"

    os.execv(target_binary, cmdline)
def _select_path_interpreter(
    path=None,  # type: Optional[str]
    valid_basenames=None,  # type: Optional[Tuple[str, ...]]
    interpreter_constraints=None,  # type: Optional[Iterable[str]]
):
    # type: (...) -> Optional[PythonInterpreter]
    candidate_interpreters_iter = iter_compatible_interpreters(
        path=path,
        valid_basenames=valid_basenames,
        interpreter_constraints=interpreter_constraints,
    )
    current_interpreter = PythonInterpreter.get()  # type: PythonInterpreter
    candidate_interpreters = []
    for interpreter in candidate_interpreters_iter:
        if current_interpreter == interpreter:
            # Always prefer continuing with the current interpreter when possible to avoid re-exec
            # overhead.
            return current_interpreter
        else:
            candidate_interpreters.append(interpreter)
    if not candidate_interpreters:
        return None

    # TODO: Allow the selection strategy to be parameterized:
    #   https://github.com/pantsbuild/pex/issues/430
    return PythonInterpreter.latest_release_of_min_compatible_version(candidate_interpreters)
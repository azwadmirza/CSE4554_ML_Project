def run_and_get_interpreter_info(name, executable):
    assert executable
    try:
        result = exec_on_interpreter(str(executable), VERSION_QUERY_SCRIPT)
        result["version_info"] = tuple(result["version_info"])  # fix json dump transformation
        del result["name"]
        del result["version"]
    except ExecFailed as e:
        return NoInterpreterInfo(name, executable=e.executable, out=e.out, err=e.err)
    else:
        return InterpreterInfo(name, **result)
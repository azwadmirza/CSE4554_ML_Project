def which(command, location=None, allow_global=False):
    if not allow_global and location is None:
        if project.virtualenv_exists:
            location = project.virtualenv_location
        else:
            location = os.environ.get("VIRTUAL_ENV", None)
    if not (location and os.path.exists(location)) and not allow_global:
        raise RuntimeError("location not created nor specified")
    if not allow_global:
        if os.name == "nt":
            p = find_windows_executable(os.path.join(location, "Scripts"), command)
        else:
            p = os.path.join(location, "bin", command)
    else:
        if command == "python":
            p = sys.executable
    if not os.path.exists(p):
        if command == "python":
            p = sys.executable or system_which("python")
        else:
            p = system_which(command)
    return p
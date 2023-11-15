def get_build_info(folder):
    toml_file = folder.join("pyproject.toml")

    # as per https://www.python.org/dev/peps/pep-0517/

    def abort(message):
        reporter.error("{} inside {}".format(message, toml_file))
        raise SystemExit(1)

    if not toml_file.exists():
        reporter.error("missing {}".format(toml_file))
        raise SystemExit(1)

    config_data = get_py_project_toml(toml_file)

    if "build-system" not in config_data:
        abort("build-system section missing")

    build_system = config_data["build-system"]

    if "requires" not in build_system:
        abort("missing requires key at build-system section")
    if "build-backend" not in build_system:
        abort("missing build-backend key at build-system section")

    requires = build_system["requires"]
    if not isinstance(requires, list) or not all(isinstance(i, six.text_type) for i in requires):
        abort("requires key at build-system section must be a list of string")

    backend = build_system["build-backend"]
    if not isinstance(backend, six.text_type):
        abort("build-backend key at build-system section must be a string")

    args = backend.split(":")
    module = args[0]
    obj = args[1] if len(args) > 1 else ""

    backend_paths = build_system.get("backend-path", [])
    if not isinstance(backend_paths, list):
        abort("backend-path key at build-system section must be a list, if specified")
    backend_paths = [folder.join(p) for p in backend_paths]

    return BuildInfo(requires, module, obj, backend_paths)
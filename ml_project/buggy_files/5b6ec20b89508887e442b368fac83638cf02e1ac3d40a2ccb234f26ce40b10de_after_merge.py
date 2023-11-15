def venv_resolve_deps(
    deps,
    which,
    project,
    pre=False,
    clear=False,
    allow_global=False,
    pypi_mirror=None,
    dev=False,
    pipfile=None,
    lockfile=None,
    keep_outdated=False
):
    """
    Resolve dependencies for a pipenv project, acts as a portal to the target environment.

    Regardless of whether a virtual environment is present or not, this will spawn
    a subproces which is isolated to the target environment and which will perform
    dependency resolution.  This function reads the output of that call and mutates
    the provided lockfile accordingly, returning nothing.

    :param List[:class:`~requirementslib.Requirement`] deps: A list of dependencies to resolve.
    :param Callable which: [description]
    :param project: The pipenv Project instance to use during resolution
    :param Optional[bool] pre: Whether to resolve pre-release candidates, defaults to False
    :param Optional[bool] clear: Whether to clear the cache during resolution, defaults to False
    :param Optional[bool] allow_global: Whether to use *sys.executable* as the python binary, defaults to False
    :param Optional[str] pypi_mirror: A URL to substitute any time *pypi.org* is encountered, defaults to None
    :param Optional[bool] dev: Whether to target *dev-packages* or not, defaults to False
    :param pipfile: A Pipfile section to operate on, defaults to None
    :type pipfile: Optional[Dict[str, Union[str, Dict[str, bool, List[str]]]]]
    :param Dict[str, Any] lockfile: A project lockfile to mutate, defaults to None
    :param bool keep_outdated: Whether to retain outdated dependencies and resolve with them in mind, defaults to False
    :raises RuntimeError: Raised on resolution failure
    :return: Nothing
    :rtype: None
    """

    from .vendor.vistir.misc import fs_str
    from .vendor.vistir.compat import Path, JSONDecodeError, NamedTemporaryFile
    from .vendor.vistir.path import create_tracked_tempdir
    from . import resolver
    from ._compat import decode_for_output
    import json

    results = []
    pipfile_section = "dev-packages" if dev else "packages"
    lockfile_section = "develop" if dev else "default"
    if not deps:
        if not project.pipfile_exists:
            return None
        deps = project.parsed_pipfile.get(pipfile_section, {})
    if not deps:
        return None

    if not pipfile:
        pipfile = getattr(project, pipfile_section, {})
    if not lockfile:
        lockfile = project._lockfile
    req_dir = create_tracked_tempdir(prefix="pipenv", suffix="requirements")
    cmd = [
        which("python", allow_global=allow_global),
        Path(resolver.__file__.rstrip("co")).as_posix()
    ]
    if pre:
        cmd.append("--pre")
    if clear:
        cmd.append("--clear")
    if allow_global:
        cmd.append("--system")
    if dev:
        cmd.append("--dev")
    target_file = NamedTemporaryFile(prefix="resolver", suffix=".json", delete=False)
    target_file.close()
    cmd.extend(["--write", make_posix(target_file.name)])
    with temp_environ():
        os.environ.update({fs_str(k): fs_str(val) for k, val in os.environ.items()})
        if pypi_mirror:
            os.environ["PIPENV_PYPI_MIRROR"] = str(pypi_mirror)
        os.environ["PIPENV_VERBOSITY"] = str(environments.PIPENV_VERBOSITY)
        os.environ["PIPENV_REQ_DIR"] = fs_str(req_dir)
        os.environ["PIP_NO_INPUT"] = fs_str("1")
        pipenv_site_dir = get_pipenv_sitedir()
        if pipenv_site_dir is not None:
            os.environ["PIPENV_SITE_DIR"] = pipenv_site_dir
        else:
            os.environ.pop("PIPENV_SITE_DIR", None)
        if keep_outdated:
            os.environ["PIPENV_KEEP_OUTDATED"] = fs_str("1")
        with create_spinner(text=decode_for_output("Locking...")) as sp:
            # This conversion is somewhat slow on local and file-type requirements since
            # we now download those requirements / make temporary folders to perform
            # dependency resolution on them, so we are including this step inside the
            # spinner context manager for the UX improvement
            sp.write(decode_for_output("Building requirements..."))
            deps = convert_deps_to_pip(
                deps, project, r=False, include_index=True
            )
            constraints = set(deps)
            os.environ["PIPENV_PACKAGES"] = str("\n".join(constraints))
            sp.write(decode_for_output("Resolving dependencies..."))
            c = resolve(cmd, sp)
            results = c.out.strip()
            if c.ok:
                sp.green.ok(environments.PIPENV_SPINNER_OK_TEXT.format("Success!"))
                if c.out.strip():
                    click_echo(crayons.yellow("Warning: {0}".format(c.out.strip())), err=True)
            else:
                sp.red.fail(environments.PIPENV_SPINNER_FAIL_TEXT.format("Locking Failed!"))
                click_echo("Output: {0}".format(c.out.strip()), err=True)
                click_echo("Error: {0}".format(c.err.strip()), err=True)
    try:
        with open(target_file.name, "r") as fh:
            results = json.load(fh)
    except (IndexError, JSONDecodeError):
        click_echo(c.out.strip(), err=True)
        click_echo(c.err.strip(), err=True)
        if os.path.exists(target_file.name):
            os.unlink(target_file.name)
        raise RuntimeError("There was a problem with locking.")
    if os.path.exists(target_file.name):
        os.unlink(target_file.name)
    if lockfile_section not in lockfile:
        lockfile[lockfile_section] = {}
    prepare_lockfile(results, pipfile, lockfile[lockfile_section])
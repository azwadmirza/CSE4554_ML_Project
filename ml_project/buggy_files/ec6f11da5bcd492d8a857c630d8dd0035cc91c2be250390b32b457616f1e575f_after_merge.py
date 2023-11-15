def pip_install(
    requirement=None,
    r=None,
    allow_global=False,
    ignore_hashes=False,
    no_deps=True,
    block=True,
    index=None,
    pre=False,
    selective_upgrade=False,
    requirements_dir=None,
    extra_indexes=None,
    pypi_mirror=None,
    trusted_hosts=None,
    use_pep517=True
):
    from pipenv.patched.notpip._internal import logger as piplogger
    from .vendor.vistir.compat import Mapping
    from .vendor.urllib3.util import parse_url
    src = []
    write_to_tmpfile = False
    if requirement:
        needs_hashes = not requirement.editable and not ignore_hashes and r is None
        has_subdir = requirement.is_vcs and requirement.req.subdirectory
        write_to_tmpfile = needs_hashes or has_subdir

    if not trusted_hosts:
        trusted_hosts = []
    trusted_hosts.extend(os.environ.get("PIP_TRUSTED_HOSTS", []))
    if environments.is_verbose():
        piplogger.setLevel(logging.INFO)
        if requirement:
            click.echo(
                crayons.normal("Installing {0!r}".format(requirement.name), bold=True),
                err=True,
            )

    if requirement:
        ignore_hashes = True if not requirement.hashes else ignore_hashes

    # Create files for hash mode.
    if write_to_tmpfile:
        if not requirements_dir:
            requirements_dir = vistir.path.create_tracked_tempdir(
                prefix="pipenv", suffix="requirements")
        f = vistir.compat.NamedTemporaryFile(
            prefix="pipenv-", suffix="-requirement.txt", dir=requirements_dir,
            delete=False
        )
        line = requirement.as_line(include_hashes=not ignore_hashes)
        f.write(vistir.misc.to_bytes(line))
        r = f.name
        f.close()

    if requirement and requirement.vcs:
        # Install dependencies when a package is a non-editable VCS dependency.
        # Don't specify a source directory when using --system.
        if not allow_global and ("PIP_SRC" not in os.environ):
            src.extend(["--src", "{0}".format(project.virtualenv_src_location)])

    # Try installing for each source in project.sources.
    if index:
        if isinstance(index, (Mapping, dict)):
            index_source = index
        else:
            try:
                index_source = project.find_source(index)
                index_source = index_source.copy()
            except SourceNotFound:
                src_name = project.src_name_from_url(index)
                index_url = parse_url(index)
                verify_ssl = index_url.host not in trusted_hosts
                index_source = {"url": index, "verify_ssl": verify_ssl, "name": src_name}
        sources = [index_source.copy(),]
        if extra_indexes:
            if isinstance(extra_indexes, six.string_types):
                extra_indexes = [extra_indexes,]
            for idx in extra_indexes:
                extra_src = None
                if isinstance(idx, (Mapping, dict)):
                    extra_src = idx
                try:
                    extra_src = project.find_source(idx) if not extra_src else extra_src
                except SourceNotFound:
                    src_name = project.src_name_from_url(idx)
                    src_url = parse_url(idx)
                    verify_ssl = src_url.host not in trusted_hosts
                    extra_src = {"url": idx, "verify_ssl": verify_ssl, "name": extra_src}
                if extra_src["url"] != index_source["url"]:
                    sources.append(extra_src)
        else:
            for idx in project.pipfile_sources:
                if idx["url"] != sources[0]["url"]:
                    sources.append(idx)
    else:
        sources = project.pipfile_sources
    if pypi_mirror:
        sources = [
            create_mirror_source(pypi_mirror) if is_pypi_url(source["url"]) else source
            for source in sources
        ]

    line_kwargs = {"as_list": True, "include_hashes": not ignore_hashes}

    # Install dependencies when a package is a VCS dependency.
    if requirement and requirement.vcs:
        ignore_hashes = True
        # Don't specify a source directory when using --system.
        src_dir = None
        if "PIP_SRC" in os.environ:
            src_dir = os.environ["PIP_SRC"]
            src = ["--src", os.environ["PIP_SRC"]]
        if not requirement.editable:
            no_deps = False

        if src_dir is not None:
            repo = requirement.req.get_vcs_repo(src_dir=src_dir)
        else:
            repo = requirement.req.get_vcs_repo()
        write_to_tmpfile = True
        line_kwargs["include_markers"] = False
        line_kwargs["include_hashes"] = False
        if not requirements_dir:
            requirements_dir = vistir.path.create_tracked_tempdir(prefix="pipenv",
                                                                  suffix="requirements")
        f = vistir.compat.NamedTemporaryFile(
            prefix="pipenv-", suffix="-requirement.txt", dir=requirements_dir,
            delete=False
        )
        line = "-e" if requirement.editable else ""
        if requirement.editable or requirement.name is not None:
            name = requirement.name
            if requirement.extras:
                name = "{0}{1}".format(name, requirement.extras_as_pip)
            line = "-e {0}#egg={1}".format(vistir.path.path_to_url(repo.checkout_directory), requirement.name)
            if repo.subdirectory:
                line = "{0}&subdirectory={1}".format(line, repo.subdirectory)
        else:
            line = requirement.as_line(**line_kwargs)
        f.write(vistir.misc.to_bytes(line))
        r = f.name
        f.close()

    # Create files for hash mode.
    if write_to_tmpfile and not r:
        if not requirements_dir:
            requirements_dir = vistir.path.create_tracked_tempdir(
                prefix="pipenv", suffix="requirements")
        f = vistir.compat.NamedTemporaryFile(
            prefix="pipenv-", suffix="-requirement.txt", dir=requirements_dir,
            delete=False
        )
        ignore_hashes = True if not requirement.hashes else ignore_hashes
        line = requirement.as_line(include_hashes=not ignore_hashes)
        line = "{0} {1}".format(line, " ".join(src))
        f.write(vistir.misc.to_bytes(line))
        r = f.name
        f.close()

    if (requirement and requirement.editable) and not r:
        line_kwargs["include_markers"] = False
        line_kwargs["include_hashes"] = False
        install_reqs = requirement.as_line(**line_kwargs)
        if requirement.editable and install_reqs[0].startswith("-e "):
            req, install_reqs = install_reqs[0], install_reqs[1:]
            possible_hashes = install_reqs[:]
            editable_opt, req = req.split(" ", 1)
            install_reqs = [editable_opt, req] + install_reqs

        # hashes must be passed via a file
        ignore_hashes = True
    elif r:
        install_reqs = ["-r", r]
        with open(r) as f:
            if "--hash" not in f.read():
                ignore_hashes = True
    else:
        ignore_hashes = True if not requirement.hashes else False
        install_reqs = requirement.as_line(as_list=True)
        if not requirement.markers:
            install_reqs = [escape_cmd(r) for r in install_reqs]
        elif len(install_reqs) > 1:
            install_reqs = install_reqs[0] + [escape_cmd(r) for r in install_reqs[1:]]
    pip_command = [which_pip(allow_global=allow_global), "install"]
    if pre:
        pip_command.append("--pre")
    if src:
        pip_command.extend(src)
    if environments.is_verbose():
        pip_command.append("--verbose")
    pip_command.append("--upgrade")
    if selective_upgrade:
        pip_command.append("--upgrade-strategy=only-if-needed")
    if no_deps:
        pip_command.append("--no-deps")
    pip_command.extend(install_reqs)
    pip_command.extend(prepare_pip_source_args(sources))
    if not ignore_hashes:
        pip_command.append("--require-hashes")
    if not use_pep517:
        from .vendor.packaging.version import parse as parse_version
        pip_command.append("--no-build-isolation")
        if project.environment.pip_version >= parse_version("19.0"):
            pip_command.append("--no-use-pep517")
    if environments.is_verbose():
        click.echo("$ {0}".format(pip_command), err=True)
    cache_dir = vistir.compat.Path(PIPENV_CACHE_DIR)
    pip_config = {
        "PIP_CACHE_DIR": vistir.misc.fs_str(cache_dir.as_posix()),
        "PIP_WHEEL_DIR": vistir.misc.fs_str(cache_dir.joinpath("wheels").as_posix()),
        "PIP_DESTINATION_DIR": vistir.misc.fs_str(
            cache_dir.joinpath("pkgs").as_posix()
        ),
        "PIP_EXISTS_ACTION": vistir.misc.fs_str("w"),
        "PATH": vistir.misc.fs_str(os.environ.get("PATH")),
    }
    if src:
        pip_config.update(
            {"PIP_SRC": vistir.misc.fs_str(project.virtualenv_src_location)}
        )
    cmd = Script.parse(pip_command)
    pip_command = cmd.cmdify()
    c = None
    # with project.environment.activated():
    c = delegator.run(pip_command, block=block, env=pip_config)
    return c
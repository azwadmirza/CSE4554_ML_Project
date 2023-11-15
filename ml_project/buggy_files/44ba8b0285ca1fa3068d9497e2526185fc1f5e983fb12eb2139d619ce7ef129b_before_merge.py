def pip_install(
    package_name=None,
    r=None,
    allow_global=False,
    ignore_hashes=False,
    no_deps=True,
    verbose=False,
    block=True,
    index=None,
    pre=False,
    selective_upgrade=False,
    requirements_dir=None,
    extra_indexes=None,
    pypi_mirror=None,
):
    from notpip._internal import logger as piplogger
    from notpip._vendor.pyparsing import ParseException
    from .vendor.requirementslib import Requirement

    if verbose:
        click.echo(
            crayons.normal("Installing {0!r}".format(package_name), bold=True), err=True
        )
        piplogger.setLevel(logging.INFO)
    # Create files for hash mode.
    if not package_name.startswith("-e ") and (not ignore_hashes) and (r is None):
        fd, r = tempfile.mkstemp(
            prefix="pipenv-", suffix="-requirement.txt", dir=requirements_dir
        )
        with os.fdopen(fd, "w") as f:
            f.write(package_name)
    # Install dependencies when a package is a VCS dependency.
    try:
        req = Requirement.from_line(
            package_name.split("--hash")[0].split("--trusted-host")[0]
        ).vcs
    except (ParseException, ValueError) as e:
        click.echo("{0}: {1}".format(crayons.red("WARNING"), e), err=True)
        click.echo(
            "{0}… You will have to reinstall any packages that failed to install.".format(
                crayons.red("ABORTING INSTALL")
            ),
            err=True,
        )
        click.echo(
            "You may have to manually run {0} when you are finished.".format(
                crayons.normal("pipenv lock", bold=True)
            )
        )
        sys.exit(1)
    if req:
        no_deps = False
        # Don't specify a source directory when using --system.
        if not allow_global and ("PIP_SRC" not in os.environ):
            src = "--src {0}".format(
                escape_grouped_arguments(project.virtualenv_src_location)
            )
        else:
            src = ""
    else:
        src = ""

    # Try installing for each source in project.sources.
    if index:
        if not is_valid_url(index):
            index = project.find_source(index).get("url")
        sources = [{"url": index}]
        if extra_indexes:
            if isinstance(extra_indexes, six.string_types):
                extra_indexes = [extra_indexes]
            for idx in extra_indexes:
                try:
                    extra_src = project.find_source(idx).get("url")
                except SourceNotFound:
                    extra_src = idx
                if extra_src != index:
                    sources.append({"url": extra_src})
        else:
            for idx in project.pipfile_sources:
                if idx["url"] != sources[0]["url"]:
                    sources.append({"url": idx["url"]})
    else:
        sources = project.pipfile_sources
    if pypi_mirror:
        sources = [
            create_mirror_source(pypi_mirror) if is_pypi_url(source["url"]) else source
            for source in sources
        ]
    if package_name.startswith("-e "):
        install_reqs = ' -e "{0}"'.format(package_name.split("-e ")[1])
    elif r:
        install_reqs = " -r {0}".format(escape_grouped_arguments(r))
    else:
        install_reqs = ' "{0}"'.format(package_name)
    # Skip hash-checking mode, when appropriate.
    if r:
        with open(r) as f:
            if "--hash" not in f.read():
                ignore_hashes = True
    else:
        if "--hash" not in install_reqs:
            ignore_hashes = True
    verbose_flag = "--verbose" if verbose else ""
    if not ignore_hashes:
        install_reqs += " --require-hashes"
    no_deps = "--no-deps" if no_deps else ""
    pre = "--pre" if pre else ""
    quoted_pip = which_pip(allow_global=allow_global)
    quoted_pip = escape_grouped_arguments(quoted_pip)
    upgrade_strategy = (
        "--upgrade --upgrade-strategy=only-if-needed" if selective_upgrade else ""
    )
    pip_command = "{0} install {4} {5} {6} {7} {3} {1} {2} --exists-action w".format(
        quoted_pip,
        install_reqs,
        " ".join(prepare_pip_source_args(sources)),
        no_deps,
        pre,
        src,
        verbose_flag,
        upgrade_strategy,
    )
    if verbose:
        click.echo("$ {0}".format(pip_command), err=True)
    cache_dir = Path(PIPENV_CACHE_DIR)
    pip_config = {
        "PIP_CACHE_DIR": fs_str(cache_dir.as_posix()),
        "PIP_WHEEL_DIR": fs_str(cache_dir.joinpath("wheels").as_posix()),
        "PIP_DESTINATION_DIR": fs_str(cache_dir.joinpath("pkgs").as_posix()),
    }
    c = delegator.run(pip_command, block=block, env=pip_config)
    return c
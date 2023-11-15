def ensure_project(
    three=None,
    python=None,
    validate=True,
    system=False,
    warn=True,
    site_packages=False,
    deploy=False,
    skip_requirements=False,
    pypi_mirror=None,
    clear=False,
):
    """Ensures both Pipfile and virtualenv exist for the project."""
    from .environments import PIPENV_USE_SYSTEM

    # Clear the caches, if appropriate.
    if clear:
        print("clearing")
        sys.exit(1)

    # Automatically use an activated virtualenv.
    if PIPENV_USE_SYSTEM:
        system = True
    if not project.pipfile_exists and deploy:
        raise exceptions.PipfileNotFound
    # Fail if working under /
    if not project.name:
        click.echo(
            "{0}: Pipenv is not intended to work under the root directory, "
            "please choose another path.".format(crayons.red("ERROR")),
            err=True
        )
        sys.exit(1)
    # Skip virtualenv creation when --system was used.
    if not system:
        ensure_virtualenv(
            three=three,
            python=python,
            site_packages=site_packages,
            pypi_mirror=pypi_mirror,
        )
        if warn:
            # Warn users if they are using the wrong version of Python.
            if project.required_python_version:
                path_to_python = which("python") or which("py")
                if path_to_python and project.required_python_version not in (
                    python_version(path_to_python) or ""
                ):
                    click.echo(
                        "{0}: Your Pipfile requires {1} {2}, "
                        "but you are using {3} ({4}).".format(
                            crayons.red("Warning", bold=True),
                            crayons.normal("python_version", bold=True),
                            crayons.blue(project.required_python_version),
                            crayons.blue(python_version(path_to_python) or "unknown"),
                            crayons.green(shorten_path(path_to_python)),
                        ),
                        err=True,
                    )
                    click.echo(
                        "  {0} and rebuilding the virtual environment "
                        "may resolve the issue.".format(crayons.green("$ pipenv --rm")),
                        err=True,
                    )
                    if not deploy:
                        click.echo(
                            "  {0} will surely fail."
                            "".format(crayons.red("$ pipenv check")),
                            err=True,
                        )
                    else:
                        raise exceptions.DeployException
    # Ensure the Pipfile exists.
    ensure_pipfile(
        validate=validate, skip_requirements=skip_requirements, system=system
    )
def do_check(
    three=None,
    python=False,
    system=False,
    unused=False,
    ignore=None,
    args=None,
    pypi_mirror=None,
):
    from pipenv.vendor.vistir.compat import JSONDecodeError
    if not system:
        # Ensure that virtualenv is available.
        ensure_project(
            three=three,
            python=python,
            validate=False,
            warn=False,
            pypi_mirror=pypi_mirror,
        )
    if not args:
        args = []
    if unused:
        deps_required = [k for k in project.packages.keys()]
        deps_needed = import_from_code(unused)
        for dep in deps_needed:
            try:
                deps_required.remove(dep)
            except ValueError:
                pass
        if deps_required:
            click.echo(
                crayons.normal(
                    "The following dependencies appear unused, and may be safe for removal:"
                )
            )
            for dep in deps_required:
                click.echo("  - {0}".format(crayons.green(dep)))
            sys.exit(1)
        else:
            sys.exit(0)
    click.echo(crayons.normal(decode_for_output("Checking PEP 508 requirements…"), bold=True))
    pep508checker_path = pep508checker.__file__.rstrip("cdo")
    safety_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "patched", "safety.zip"
    )
    if not system:
        python = which("python")
    else:
        python = system_which("python")
    _cmd = [python,]
    # Run the PEP 508 checker in the virtualenv.
    cmd = _cmd + [pep508checker_path]
    c = run_command(cmd)
    try:
        results = simplejson.loads(c.out.strip())
    except JSONDecodeError:
        click.echo("{0}\n{1}".format(
            crayons.white(decode_for_output("Failed parsing pep508 results: "), bold=True),
            c.out.strip()
        ))
        sys.exit(1)
    # Load the pipfile.
    p = pipfile.Pipfile.load(project.pipfile_location)
    failed = False
    # Assert each specified requirement.
    for marker, specifier in p.data["_meta"]["requires"].items():
        if marker in results:
            try:
                assert results[marker] == specifier
            except AssertionError:
                failed = True
                click.echo(
                    "Specifier {0} does not match {1} ({2})."
                    "".format(
                        crayons.green(marker),
                        crayons.blue(specifier),
                        crayons.red(results[marker]),
                    ),
                    err=True,
                )
    if failed:
        click.echo(crayons.red("Failed!"), err=True)
        sys.exit(1)
    else:
        click.echo(crayons.green("Passed!"))
    click.echo(crayons.normal(
        decode_for_output("Checking installed package safety…"), bold=True)
    )
    if ignore:
        ignored = "--ignore {0}".format(" --ignore ".join(ignore))
        click.echo(
            crayons.normal(
                "Notice: Ignoring CVE(s) {0}".format(crayons.yellow(", ".join(ignore)))
            ),
            err=True,
        )
    else:
        ignored = ""
    key = "--key={0}".format(PIPENV_PYUP_API_KEY)
    cmd = _cmd + [safety_path, "check", "--json", key, ignored]
    c = run_command(cmd)
    try:
        results = simplejson.loads(c.out)
    except (ValueError, JSONDecodeError):
        raise exceptions.JSONParseError(c.out, c.err)
    for (package, resolved, installed, description, vuln) in results:
        click.echo(
            "{0}: {1} {2} resolved ({3} installed)!".format(
                crayons.normal(vuln, bold=True),
                crayons.green(package),
                crayons.red(resolved, bold=False),
                crayons.red(installed, bold=True),
            )
        )
        click.echo("{0}".format(description))
        click.echo()
    if not results:
        click.echo(crayons.green("All good!"))
    else:
        sys.exit(1)
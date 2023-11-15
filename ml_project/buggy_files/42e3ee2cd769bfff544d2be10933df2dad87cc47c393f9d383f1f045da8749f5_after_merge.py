def do_graph(bare=False, json=False, json_tree=False, reverse=False):
    from pipenv.vendor.vistir.compat import JSONDecodeError
    import pipdeptree
    pipdeptree_path = pipdeptree.__file__.rstrip("cdo")
    try:
        python_path = which("python")
    except AttributeError:
        click.echo(
            u"{0}: {1}".format(
                crayons.red("Warning", bold=True),
                u"Unable to display currently-installed dependency graph information here. "
                u"Please run within a Pipenv project.",
            ),
            err=True,
        )
        sys.exit(1)
    except RuntimeError:
        pass

    if reverse and json:
        click.echo(
            u"{0}: {1}".format(
                crayons.red("Warning", bold=True),
                u"Using both --reverse and --json together is not supported. "
                u"Please select one of the two options.",
            ),
            err=True,
        )
        sys.exit(1)
    if reverse and json_tree:
        click.echo(
            u"{0}: {1}".format(
                crayons.red("Warning", bold=True),
                u"Using both --reverse and --json-tree together is not supported. "
                u"Please select one of the two options.",
            ),
            err=True,
        )
        sys.exit(1)
    if json and json_tree:
        click.echo(
            u"{0}: {1}".format(
                crayons.red("Warning", bold=True),
                u"Using both --json and --json-tree together is not supported. "
                u"Please select one of the two options.",
            ),
            err=True,
        )
        sys.exit(1)
    flag = ""
    if json:
        flag = "--json"
    if json_tree:
        flag = "--json-tree"
    if reverse:
        flag = "--reverse"
    if not project.virtualenv_exists:
        click.echo(
            u"{0}: No virtualenv has been created for this project yet! Consider "
            u"running {1} first to automatically generate one for you or see "
            u"{2} for further instructions.".format(
                crayons.red("Warning", bold=True),
                crayons.green("`pipenv install`"),
                crayons.green("`pipenv install --help`"),
            ),
            err=True,
        )
        sys.exit(1)
    cmd_args = [python_path, pipdeptree_path, flag, "-l"]
    c = run_command(cmd_args)
    # Run dep-tree.
    if not bare:
        if json:
            data = []
            for d in simplejson.loads(c.out):
                if d["package"]["key"] not in BAD_PACKAGES:
                    data.append(d)
            click.echo(simplejson.dumps(data, indent=4))
            sys.exit(0)
        elif json_tree:

            def traverse(obj):
                if isinstance(obj, list):
                    return [
                        traverse(package)
                        for package in obj
                        if package["key"] not in BAD_PACKAGES
                    ]
                else:
                    obj["dependencies"] = traverse(obj["dependencies"])
                    return obj

            try:
                parsed = simplejson.loads(c.out.strip())
            except JSONDecodeError:
                raise exceptions.JSONParseError(c.out, c.err)
            else:
                data = traverse(parsed)
                click.echo(simplejson.dumps(data, indent=4))
                sys.exit(0)
        else:
            for line in c.out.strip().split("\n"):
                # Ignore bad packages as top level.
                if line.split("==")[0] in BAD_PACKAGES and not reverse:
                    continue

                # Bold top-level packages.
                if not line.startswith(" "):
                    click.echo(crayons.normal(line, bold=True))
                # Echo the rest.
                else:
                    click.echo(crayons.normal(line, bold=False))
    else:
        click.echo(c.out)
    if c.return_code != 0:
        click.echo(
            "{0} {1}".format(
                crayons.red("ERROR: ", bold=True),
                crayons.white("{0}".format(c.err, bold=True)),
            ),
            err=True,
        )
    # Return its return code.
    sys.exit(c.return_code)
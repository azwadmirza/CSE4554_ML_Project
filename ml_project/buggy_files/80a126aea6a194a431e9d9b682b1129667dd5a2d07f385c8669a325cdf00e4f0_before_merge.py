def _lint(session, rcfile, flags, paths):
    _install_requirements(session, 'zeromq')
    session.install('--progress-bar=off', '-r', 'requirements/static/{}/lint.txt'.format(_get_pydir(session)), silent=PIP_INSTALL_SILENT)
    session.run('pylint', '--version')
    pylint_report_path = os.environ.get('PYLINT_REPORT')

    cmd_args = [
        'pylint',
        '--rcfile={}'.format(rcfile)
    ] + list(flags) + list(paths)

    stdout = tempfile.TemporaryFile(mode='w+b')
    lint_failed = False
    try:
        session.run(*cmd_args, stdout=stdout)
    except CommandFailed:
        lint_failed = True
        raise
    finally:
        stdout.seek(0)
        contents = stdout.read().encode('utf-8')
        if contents:
            sys.stdout.write(contents)
            sys.stdout.flush()
            if pylint_report_path:
                # Write report
                with open(pylint_report_path, 'w') as wfh:
                    wfh.write(contents)
                session.log('Report file written to %r', pylint_report_path)
        stdout.close()
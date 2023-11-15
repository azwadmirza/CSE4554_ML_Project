def main(argv=None):
    argv = argv or sys.argv
    assert len(argv) >= 3
    assert argv[1].startswith('shell.')
    shell = argv[1].replace('shell.', '', 1)
    activator_args = argv[2:]
    activator = Activator(shell, activator_args)
    try:
        sys.stdout.write(activator.execute())
        return 0
    except Exception as e:
        from . import CondaError
        if isinstance(e, CondaError):
            sys.stderr.write(text_type(e))
            return e.return_code
        else:
            raise
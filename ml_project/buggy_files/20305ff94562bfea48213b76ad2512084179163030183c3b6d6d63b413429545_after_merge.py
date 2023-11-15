def main(argv=None):
    argv = argv or sys.argv
    assert len(argv) >= 3
    assert argv[1].startswith('shell.')
    shell = argv[1].replace('shell.', '', 1)
    activator_args = argv[2:]
    activator = Activator(shell, activator_args)
    try:
        print(activator.execute(), end='')
        return 0
    except Exception as e:
        from . import CondaError
        if isinstance(e, CondaError):
            print(text_type(e), file=sys.stderr)
            return e.return_code
        else:
            raise
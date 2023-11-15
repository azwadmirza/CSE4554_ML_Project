def _find_by_py_launcher(
        version: str,
) -> Optional[str]:  # pragma: no cover (windows only)
    if version.startswith('python'):
        num = version[len('python'):]
        try:
            cmd = ('py', f'-{num}', '-c', 'import sys; print(sys.executable)')
            return cmd_output(*cmd)[1].strip()
        except CalledProcessError:
            pass
    return None
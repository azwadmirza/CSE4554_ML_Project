def _find_by_py_launcher(
        version: str,
) -> Optional[str]:  # pragma: no cover (windows only)
    if version.startswith('python'):
        num = version[len('python'):]
        cmd = ('py', f'-{num}', '-c', 'import sys; print(sys.executable)')
        env = dict(os.environ, PYTHONIOENCODING='UTF-8')
        try:
            return cmd_output(*cmd, env=env)[1].strip()
        except CalledProcessError:
            pass
    return None
def _get_session_python_version_info(session):
    try:
        version_info = session._runner._real_python_version_info
    except AttributeError:
        session_py_version = session.run(
            'python', '-c'
            'import sys; sys.stdout.write("{}.{}.{}".format(*sys.version_info))',
            silent=True,
            log=False,
            bypass_install_only=True
        )
        version_info = tuple(int(part) for part in session_py_version.split('.') if part.isdigit())
        session._runner._real_python_version_info = version_info
    return version_info
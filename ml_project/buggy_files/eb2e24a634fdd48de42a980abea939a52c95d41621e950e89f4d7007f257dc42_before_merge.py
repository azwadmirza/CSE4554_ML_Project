def _get_session_python_site_packages_dir(session):
    try:
        site_packages_dir = session._runner._site_packages_dir
    except AttributeError:
        site_packages_dir = session.run(
            'python', '-c'
            'import sys; from distutils.sysconfig import get_python_lib; sys.stdout.write(get_python_lib())',
            silent=True,
            log=False,
            bypass_install_only=True
        )
        session._runner._site_packages_dir = site_packages_dir
    return site_packages_dir
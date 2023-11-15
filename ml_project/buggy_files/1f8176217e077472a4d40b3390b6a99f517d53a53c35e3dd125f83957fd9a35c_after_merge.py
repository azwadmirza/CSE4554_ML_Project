def _get_distro_info(session):
    try:
        distro = session._runner._distro
    except AttributeError:
        # The distro package doesn't output anything for Windows
        old_install_only_value = session._runner.global_config.install_only
        try:
            # Force install only to be false for the following chunk of code
            # For additional information as to why see:
            #   https://github.com/theacodes/nox/pull/181
            session._runner.global_config.install_only = False
            session.install('--progress-bar=off', 'distro', silent=PIP_INSTALL_SILENT)
            output = session.run('distro', '-j', silent=True)
            distro = json.loads(output.strip())
            session.log('Distro information:\n%s', pprint.pformat(distro))
            session._runner._distro = distro
        finally:
            session._runner.global_config.install_only = old_install_only_value
    return distro
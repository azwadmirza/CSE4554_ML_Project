def _get_distro_info(session):
    try:
        distro = session._runner._distro
    except AttributeError:
        # The distro package doesn't output anything for Windows
        session.install('--progress-bar=off', 'distro', silent=PIP_INSTALL_SILENT)
        output = session.run('distro', '-j', silent=True, bypass_install_only=True)
        distro = json.loads(output.strip())
        session.log('Distro information:\n%s', pprint.pformat(distro))
        session._runner._distro = distro
    return distro
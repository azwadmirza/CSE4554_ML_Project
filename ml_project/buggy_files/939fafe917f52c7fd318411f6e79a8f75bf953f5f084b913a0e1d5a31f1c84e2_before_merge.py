def install_scripts(distributions):
    """
    Regenerate the entry_points console_scripts for the named distribution.
    """
    try:
        from pex.third_party.setuptools.command import easy_install
        import pex.third_party.pkg_resources as pkg_resources
    except ImportError:
        raise RuntimeError("'wheel install_scripts' needs setuptools.")

    for dist in distributions:
        pkg_resources_dist = pkg_resources.get_distribution(dist)
        install = get_install_command(dist)
        command = easy_install.easy_install(install.distribution)
        command.args = ['wheel']  # dummy argument
        command.finalize_options()
        command.install_egg_scripts(pkg_resources_dist)
def install_scripts(distributions):
    """
    Regenerate the entry_points console_scripts for the named distribution.
    """
    try:
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from setuptools.command import easy_install  # vendor:skip
        else:
          from pex.third_party.setuptools.command import easy_install

        if "__PEX_UNVENDORED__" in __import__("os").environ:
          import pkg_resources  # vendor:skip
        else:
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
def check_for_updates():
    """
    Checks if updates are available by reading the cached release number from the
    config file and notifies the user. Prints an update note to the command line.
    """
    from packaging.version import Version
    from maestral import __version__

    state = MaestralState('maestral')
    latest_release = state.get('app', 'latest_release')

    has_update = Version(__version__) < Version(latest_release)

    if has_update:
        click.secho(
            f'Maestral v{latest_release} has been released, you have v{__version__}. '
            f'Please use your package manager to update.', fg='orange'
        )
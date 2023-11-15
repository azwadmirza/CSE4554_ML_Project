def locale_export():
    """Exports for dealing with Click-based programs and ASCII/Unicode errors.

    RuntimeError: Click will abort further execution because Python 3 was
    configured to use ASCII as encoding for the environment.
    Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
    """
    locale_to_use = get_locale()
    return "export LC_ALL=%s && export LANG=%s && " % (locale_to_use, locale_to_use)
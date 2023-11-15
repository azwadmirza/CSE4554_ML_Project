def locale_export():
    """Exports for dealing with Click-based programs and ASCII/Unicode errors.

    RuntimeError: Click will abort further execution because Python 3 was
    configured to use ASCII as encoding for the environment.
    Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.

    Looks up available locales on the system to find an appropriate one to pick,
    defaulting to C.UTF-8 which is globally available on newer systems.
    """
    locale_to_use = "C.UTF-8"
    try:
        locales = subprocess.check_output(["locale", "-a"]).decode(errors="ignore").split("\n")
    except subprocess.CalledProcessError:
        locales = []
    for locale in locales:
        if locale.lower().endswith(("utf-8", "utf8")):
            locale_to_use = locale
            break
    return "export LC_ALL=%s && export LANG=%s && " % (locale_to_use, locale_to_use)
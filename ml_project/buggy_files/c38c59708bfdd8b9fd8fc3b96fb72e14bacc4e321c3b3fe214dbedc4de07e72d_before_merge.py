def format_std_prepost(template, env=None):
    """Formats a template prefix/postfix string for a standard buffer.
    Returns a string suitable for prepending or appending.
    """
    if not template:
        return ""
    env = builtins.__xonsh__.env if env is None else env
    shell = builtins.__xonsh__.shell.shell
    try:
        s = shell.prompt_formatter(template)
    except Exception:
        print_exception()
    # \001\002 is there to fool pygments into not returning an empty string
    # for potentially empty input. This happens when the template is just a
    # color code with no visible text.
    invis = "\001\002"
    s = shell.format_color(invis + s + invis, force_string=True)
    s = s.replace(invis, "")
    return s
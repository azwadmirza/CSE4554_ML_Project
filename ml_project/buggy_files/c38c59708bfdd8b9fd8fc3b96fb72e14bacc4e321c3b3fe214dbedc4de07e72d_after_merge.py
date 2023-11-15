def format_std_prepost(template, env=None):
    """Formats a template prefix/postfix string for a standard buffer.
    Returns a string suitable for prepending or appending.
    """
    if not template:
        return ""
    env = builtins.__xonsh__.env if env is None else env
    invis = "\001\002"
    if builtins.__xonsh__.shell is None:
        # shell hasn't fully started up (probably still in xonshrc)
        from xonsh.prompt.base import PromptFormatter
        from xonsh.ansi_colors import ansi_partial_color_format

        pf = PromptFormatter()
        s = pf(template)
        style = env.get("XONSH_COLOR_STYLE")
        s = ansi_partial_color_format(invis + s + invis, hide=False, style=style)
    else:
        # shell has fully started. do the normal thing
        shell = builtins.__xonsh__.shell.shell
        try:
            s = shell.prompt_formatter(template)
        except Exception:
            print_exception()
        # \001\002 is there to fool pygments into not returning an empty string
        # for potentially empty input. This happens when the template is just a
        # color code with no visible text.
        s = shell.format_color(invis + s + invis, force_string=True)
    s = s.replace(invis, "")
    return s
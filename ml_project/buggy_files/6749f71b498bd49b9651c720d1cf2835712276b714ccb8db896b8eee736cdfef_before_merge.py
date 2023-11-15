def render(
    template_file,
    saltenv="base",
    sls="",
    argline="",
    context=None,
    tmplpath=None,
    **kws
):
    """
    Render the template_file, passing the functions and grains into the
    Jinja rendering system.

    :rtype: string
    """
    from_str = argline == "-s"
    if not from_str and argline:
        raise SaltRenderError("Unknown renderer option: {opt}".format(opt=argline))

    tmp_data = salt.utils.templates.JINJA(
        template_file,
        to_str=True,
        salt=_split_module_dicts(),
        grains=__grains__,
        opts=__opts__,
        pillar=__pillar__,
        saltenv=saltenv,
        sls=sls,
        context=context,
        tmplpath=tmplpath,
        proxy=__proxy__,
        **kws
    )
    if not tmp_data.get("result", False):
        raise SaltRenderError(
            tmp_data.get("data", "Unknown render error in jinja renderer")
        )
    if isinstance(tmp_data["data"], bytes):
        tmp_data["data"] = tmp_data["data"].decode(__salt_system_encoding__)
    return StringIO(tmp_data["data"])
def _render(template, render, renderer, template_dict, opts):
    '''
    Render a template
    '''
    if render:
        if template_dict is None:
            template_dict = {}
        if not renderer:
            renderer = opts.get('renderer', 'yaml_jinja')
        rend = salt.loader.render(opts, {})
        blacklist = opts.get('renderer_blacklist')
        whitelist = opts.get('renderer_whitelist')
        ret = compile_template(template, rend, renderer, blacklist, whitelist, **template_dict)
        if salt.utils.stringio.is_readable(ret):
            ret = ret.read()
        if str(ret).startswith('#!') and not str(ret).startswith('#!/'):
            ret = str(ret).split('\n', 1)[1]
        return ret
    with salt.utils.fopen(template, 'r') as fh_:
        return fh_.read()
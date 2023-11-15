def render_cheetah_tmpl(tmplstr, context, tmplpath=None):
    '''
    Render a Cheetah template.
    '''
    from Cheetah.Template import Template
    return salt.utils.data.decode(Template(tmplstr, searchList=[context]))
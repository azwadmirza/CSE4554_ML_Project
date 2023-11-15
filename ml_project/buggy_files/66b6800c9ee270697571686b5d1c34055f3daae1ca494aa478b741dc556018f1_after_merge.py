def render_cheetah_tmpl(tmplstr, context, tmplpath=None):
    '''
    Render a Cheetah template.
    '''
    from Cheetah.Template import Template

    # Compile the template and render it into the class
    tclass = Template.compile(tmplstr)
    data = tclass(namespaces=[context])

    # Figure out which method to call based on the type of tmplstr
    if six.PY3 and isinstance(tmplstr, six.string_types):
        # This should call .__unicode__()
        res = str(data)
    elif six.PY2 and isinstance(tmplstr, six.text_type):
        # Expicitly call .__unicode__()
        res = data.__unicode__()
    elif isinstance(tmplstr, six.binary_type):
        # This should call .__str()
        res = str(data)
    else:
        raise SaltRenderError('Unknown type {!s} for Cheetah template while trying to render.'.format(type(tmplstr)))

    # Now we can decode it to the correct encoding
    return salt.utils.data.decode(res)
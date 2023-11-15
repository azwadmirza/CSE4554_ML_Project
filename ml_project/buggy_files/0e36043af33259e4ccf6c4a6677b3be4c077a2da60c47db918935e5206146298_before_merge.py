def render_jinja_tmpl(tmplstr, context, tmplpath=None):
    opts = context['opts']
    env = context['env']
    loader = None
    newline = False

    if tmplstr.endswith('\n'):
        newline = True

    if not env:
        if tmplpath:
            # ie, the template is from a file outside the state tree
            loader = jinja2.FileSystemLoader(
                context, os.path.dirname(tmplpath))
    else:
        loader = JinjaSaltCacheLoader(opts, context['env'])
    env_args = {'extensions': [], 'loader': loader}

    if hasattr(jinja2.ext, 'with_'):
        env_args['extensions'].append('jinja2.ext.with_')
    if hasattr(jinja2.ext, 'do'):
        env_args['extensions'].append('jinja2.ext.do')
    if hasattr(jinja2.ext, 'loopcontrols'):
        env_args['extensions'].append('jinja2.ext.loopcontrols')
    env_args['extensions'].append(JinjaSerializerExtension)

    if opts.get('allow_undefined', False):
        jinja_env = jinja2.Environment(**env_args)
    else:
        jinja_env = jinja2.Environment(
                        undefined=jinja2.StrictUndefined, **env_args)
    jinja_env.filters['strftime'] = salt.utils.date_format

    unicode_context = {}
    for key, value in context.iteritems():
        if not isinstance(value, basestring):
            unicode_context[key] = value
            continue

        # Let's try UTF-8 and fail if this still fails, that's why this is not
        # wrapped in a try/except
        unicode_context[key] = unicode(value, 'utf-8')

    try:
        output = jinja_env.from_string(tmplstr).render(**unicode_context)
        if isinstance(output, unicode):
            # Let's encode the output back to utf-8 since that's what's assumed
            # in salt
            output = output.encode('utf-8')
    except jinja2.exceptions.TemplateSyntaxError as exc:
        line = traceback.extract_tb(sys.exc_info()[2])[-1][1]
        marker = '    <======================'
        context = get_template_context(tmplstr, line, marker=marker)
        error = '{0}; line {1} in template:\n\n{2}'.format(
                exc,
                line,
                context
        )
        raise SaltTemplateRenderError(error)
    except jinja2.exceptions.UndefinedError:
        line = traceback.extract_tb(sys.exc_info()[2])[-1][1]
        marker = '    <======================'
        context = get_template_context(tmplstr, line, marker=marker)
        error = 'Undefined jinja variable; line {0} in template\n\n{1}'.format(
                line,
                context
        )
        raise SaltTemplateRenderError(error)

    # Workaround a bug in Jinja that removes the final newline
    # (https://github.com/mitsuhiko/jinja2/issues/75)
    if newline:
        output += '\n'

    return output
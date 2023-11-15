def render_jinja_tmpl(tmplstr, context, tmplpath=None):
    opts = context['opts']
    saltenv = context['saltenv']
    loader = None
    newline = False

    if tmplstr and not isinstance(tmplstr, six.text_type):
        # http://jinja.pocoo.org/docs/api/#unicode
        tmplstr = tmplstr.decode(SLS_ENCODING)

    if tmplstr.endswith('\n'):
        newline = True

    if not saltenv:
        if tmplpath:
            # i.e., the template is from a file outside the state tree
            #
            # XXX: FileSystemLoader is not being properly instantiated here is
            # it? At least it ain't according to:
            #
            #   http://jinja.pocoo.org/docs/api/#jinja2.FileSystemLoader
            loader = jinja2.FileSystemLoader(
                context, os.path.dirname(tmplpath))
    else:
        loader = salt.utils.jinja.SaltCacheLoader(opts, saltenv, pillar_rend=context.get('_pillar_rend', False))

    env_args = {'extensions': [], 'loader': loader}

    if hasattr(jinja2.ext, 'with_'):
        env_args['extensions'].append('jinja2.ext.with_')
    if hasattr(jinja2.ext, 'do'):
        env_args['extensions'].append('jinja2.ext.do')
    if hasattr(jinja2.ext, 'loopcontrols'):
        env_args['extensions'].append('jinja2.ext.loopcontrols')
    env_args['extensions'].append(salt.utils.jinja.SerializerExtension)

    # Pass through trim_blocks and lstrip_blocks Jinja parameters
    # trim_blocks removes newlines around Jinja blocks
    # lstrip_blocks strips tabs and spaces from the beginning of
    # line to the start of a block.
    if opts.get('jinja_trim_blocks', False):
        log.debug('Jinja2 trim_blocks is enabled')
        env_args['trim_blocks'] = True
    if opts.get('jinja_lstrip_blocks', False):
        log.debug('Jinja2 lstrip_blocks is enabled')
        env_args['lstrip_blocks'] = True

    if opts.get('allow_undefined', False):
        jinja_env = jinja2.Environment(**env_args)
    else:
        jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined,
                                       **env_args)

    jinja_env.filters['strftime'] = salt.utils.date_format
    jinja_env.filters['sequence'] = salt.utils.jinja.ensure_sequence_filter
    jinja_env.filters['yaml_dquote'] = salt.utils.yamlencoding.yaml_dquote
    jinja_env.filters['yaml_squote'] = salt.utils.yamlencoding.yaml_squote
    jinja_env.filters['yaml_encode'] = salt.utils.yamlencoding.yaml_encode

    jinja_env.globals['odict'] = OrderedDict
    jinja_env.globals['show_full_context'] = salt.utils.jinja.show_full_context

    jinja_env.tests['list'] = salt.utils.is_list

    decoded_context = {}
    for key, value in six.iteritems(context):
        if not isinstance(value, string_types):
            decoded_context[key] = value
            continue

        decoded_context[key] = salt.utils.locales.sdecode(value)

    try:
        template = jinja_env.from_string(tmplstr)
        template.globals.update(decoded_context)
        output = template.render(**decoded_context)
    except jinja2.exceptions.TemplateSyntaxError as exc:
        trace = traceback.extract_tb(sys.exc_info()[2])
        line, out = _get_jinja_error(trace, context=decoded_context)
        if not line:
            tmplstr = ''
        raise SaltRenderError('Jinja syntax error: {0}{1}'.format(exc, out),
                              line,
                              tmplstr)
    except jinja2.exceptions.UndefinedError as exc:
        trace = traceback.extract_tb(sys.exc_info()[2])
        out = _get_jinja_error(trace, context=decoded_context)[1]
        tmplstr = ''
        # Don't include the line number, since it is misreported
        # https://github.com/mitsuhiko/jinja2/issues/276
        raise SaltRenderError(
            'Jinja variable {0}{1}'.format(
                exc, out),
            buf=tmplstr)
    except (SaltInvocationError, CommandExecutionError) as exc:
        trace = traceback.extract_tb(sys.exc_info()[2])
        line, out = _get_jinja_error(trace, context=decoded_context)
        if not line:
            tmplstr = ''
        raise SaltRenderError(
            'Problem running salt function in Jinja template: {0}{1}'.format(
                exc, out),
            line,
            tmplstr)
    except Exception as exc:
        tracestr = traceback.format_exc()
        trace = traceback.extract_tb(sys.exc_info()[2])
        line, out = _get_jinja_error(trace, context=decoded_context)
        if not line:
            tmplstr = ''
        else:
            tmplstr += '\n{0}'.format(tracestr)
        log.debug("Jinja Error")
        log.debug("Exception: {0}".format(exc))
        log.debug("Out: {0}".format(out))
        log.debug("Line: {0}".format(line))
        log.debug("TmplStr: {0}".format(tmplstr))
        log.debug("TraceStr: {0}".format(tracestr))

        raise SaltRenderError('Jinja error: {0}{1}'.format(exc, out),
                              line,
                              tmplstr,
                              trace=tracestr)

    # Workaround a bug in Jinja that removes the final newline
    # (https://github.com/mitsuhiko/jinja2/issues/75)
    if newline:
        output += '\n'

    return output
def wrap_tmpl_func(render_str):

    def render_tmpl(tmplsrc,
                    from_str=False,
                    to_str=False,
                    context=None,
                    tmplpath=None,
                    **kws):

        if context is None:
            context = {}

        # Alias cmd.run to cmd.shell to make python_shell=True the default for
        # templated calls
        if 'salt' in kws:
            kws['salt'] = AliasedLoader(kws['salt'])

        # We want explicit context to overwrite the **kws
        kws.update(context)
        context = kws
        assert 'opts' in context
        assert 'saltenv' in context

        if 'sls' in context:
            slspath = context['sls'].replace('.', '/')
            if tmplpath is not None:
                context['tplpath'] = tmplpath
                if not tmplpath.lower().replace('\\', '/').endswith('/init.sls'):
                    slspath = os.path.dirname(slspath)
                template = tmplpath.replace('\\', '/')
                i = template.rfind(slspath.replace('.', '/'))
                if i != -1:
                    template = template[i:]
                tpldir = os.path.dirname(template).replace('\\', '/')
                tpldata = {
                    'tplfile': template,
                    'tpldir': '.' if tpldir == '' else tpldir,
                    'tpldot': tpldir.replace('/', '.'),
                }
                context.update(tpldata)
            context['slsdotpath'] = slspath.replace('/', '.')
            context['slscolonpath'] = slspath.replace('/', ':')
            context['sls_path'] = slspath.replace('/', '_')
            context['slspath'] = slspath

        if isinstance(tmplsrc, six.string_types):
            if from_str:
                tmplstr = tmplsrc
            else:
                try:
                    if tmplpath is not None:
                        tmplsrc = os.path.join(tmplpath, tmplsrc)
                    with codecs.open(tmplsrc, 'r', SLS_ENCODING) as _tmplsrc:
                        tmplstr = _tmplsrc.read()
                except (UnicodeDecodeError,
                        ValueError,
                        OSError,
                        IOError) as exc:
                    if salt.utils.files.is_binary(tmplsrc):
                        # Template is a bin file, return the raw file
                        return dict(result=True, data=tmplsrc)
                    log.error(
                        'Exception occurred while reading file %s: %s',
                        tmplsrc, exc,
                        exc_info_on_loglevel=logging.DEBUG
                    )
                    raise exc
        else:  # assume tmplsrc is file-like.
            tmplstr = tmplsrc.read()
            tmplsrc.close()
        try:
            output = render_str(tmplstr, context, tmplpath)
            if six.PY2:
                output = output.encode(SLS_ENCODING)
            if salt.utils.platform.is_windows():
                newline = False
                if salt.utils.stringutils.to_unicode(output).endswith(('\n', os.linesep)):
                    newline = True
                # Write out with Windows newlines
                output = os.linesep.join(output.splitlines())
                if newline:
                    output += os.linesep

        except SaltRenderError as exc:
            log.exception('Rendering exception occurred')
            #return dict(result=False, data=six.text_type(exc))
            raise
        except Exception:
            return dict(result=False, data=traceback.format_exc())
        else:
            if to_str:  # then render as string
                return dict(result=True, data=output)
            with tempfile.NamedTemporaryFile('wb', delete=False, prefix=salt.utils.files.TEMPFILE_PREFIX) as outf:
                if six.PY3:
                    output = output.encode(SLS_ENCODING)
                outf.write(output)
                # Note: If nothing is replaced or added by the rendering
                #       function, then the contents of the output file will
                #       be exactly the same as the input.
            return dict(result=True, data=outf.name)

    render_tmpl.render_str = render_str
    return render_tmpl
    def render_tmpl(tmplsrc, from_str=False, to_str=False,
                    context=None, tmplpath=None, **kws):
        if context is None:
            context = {}
        # We want explicit context to overwrite the **kws
        kws.update(context)
        context = kws
        assert 'opts' in context
        assert 'env' in context

        if isinstance(tmplsrc, basestring):
            if from_str:
                tmplstr = tmplsrc
            else:
                try:
                    with codecs.open(tmplsrc, 'r', SLS_ENCODING) as _tmplsrc:
                        tmplstr = _tmplsrc.read()
                except (UnicodeDecodeError, ValueError) as exc:
                    if salt.utils.is_bin_file(tmplsrc):
                        # Template is a bin file, return the raw file
                        return dict(result=True, data=tmplsrc)
                    log.error('Exception ocurred while reading file {0}: {1}'
                              .format(tmplsrc, exc))
                    raise exc
        else:  # assume tmplsrc is file-like.
            tmplstr = tmplsrc.read()
            tmplsrc.close()
        try:
            output = render_str(tmplstr, context, tmplpath)
            if salt.utils.is_windows():
                # Write out with Windows newlines
                output = os.linesep.join(output.splitlines())

        except SaltTemplateRenderError as exc:
            return dict(result=False, data=str(exc))
        except Exception:
            return dict(result=False, data=traceback.format_exc())
        else:
            if to_str:  # then render as string
                return dict(result=True, data=output)
            with tempfile.NamedTemporaryFile('wb', delete=False) as outf:
                outf.write(SLS_ENCODER(output)[0])
                # Note: If nothing is replaced or added by the rendering
                #       function, then the contents of the output file will
                #       be exactly the same as the input.
            return dict(result=True, data=outf.name)
                def _wrap_existing_dispatch(element, compiler, **kw):
                    try:
                        return existing_dispatch(element, compiler, **kw)
                    except exc.UnsupportedCompilationError as uce:
                        util.raise_(
                            exc.UnsupportedCompilationError(
                                compiler,
                                type(element),
                                message="%s construct has no default "
                                "compilation handler." % type(element),
                            ),
                            from_=uce,
                        )
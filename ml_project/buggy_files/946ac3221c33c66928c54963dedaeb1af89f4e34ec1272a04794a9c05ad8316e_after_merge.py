def validate_config_values(app):
    # type: (Sphinx) -> None
    if app.config.latex_toplevel_sectioning not in (None, 'part', 'chapter', 'section'):
        logger.warning('invalid latex_toplevel_sectioning, ignored: %s',
                       app.config.latex_toplevel_sectioning)
        app.config.latex_toplevel_sectioning = None  # type: ignore

    if 'footer' in app.config.latex_elements:
        if 'postamble' in app.config.latex_elements:
            logger.warning("latex_elements['footer'] conflicts with "
                           "latex_elements['postamble'], ignored.")
        else:
            warnings.warn("latex_elements['footer'] is deprecated. "
                          "Use latex_elements['preamble'] instead.",
                          RemovedInSphinx17Warning)
            app.config.latex_elements['postamble'] = app.config.latex_elements['footer']

    if app.config.latex_keep_old_macro_names:
        warnings.warn("latex_keep_old_macro_names is deprecated. "
                      "LaTeX markup since Sphinx 1.4.5 uses only prefixed macro names.",
                      RemovedInSphinx17Warning)

    for document in app.config.latex_documents:
        try:
            text_type(document[2])
        except UnicodeDecodeError:
            raise ConfigError(
                'Invalid latex_documents.title found (might contain non-ASCII chars. '
                'Please use u"..." notation instead): %r' % (document,)
            )

        try:
            text_type(document[3])
        except UnicodeDecodeError:
            raise ConfigError(
                'Invalid latex_documents.author found (might contain non-ASCII chars. '
                'Please use u"..." notation instead): %r' % (document,)
            )
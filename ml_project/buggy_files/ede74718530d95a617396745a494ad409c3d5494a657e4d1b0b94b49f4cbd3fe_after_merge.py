def process_generate_options(app: Sphinx) -> None:
    genfiles = app.config.autosummary_generate

    if genfiles is True:
        env = app.builder.env
        genfiles = [env.doc2path(x, base=None) for x in env.found_docs
                    if os.path.isfile(env.doc2path(x))]
    elif genfiles is False:
        pass
    else:
        ext = list(app.config.source_suffix)
        genfiles = [genfile + (ext[0] if not genfile.endswith(tuple(ext)) else '')
                    for genfile in genfiles]

        for entry in genfiles[:]:
            if not path.isfile(path.join(app.srcdir, entry)):
                logger.warning(__('autosummary_generate: file not found: %s'), entry)
                genfiles.remove(entry)

    if not genfiles:
        return

    suffix = get_rst_suffix(app)
    if suffix is None:
        logger.warning(__('autosummary generats .rst files internally. '
                          'But your source_suffix does not contain .rst. Skipped.'))
        return

    from sphinx.ext.autosummary.generate import generate_autosummary_docs

    imported_members = app.config.autosummary_imported_members
    with mock(app.config.autosummary_mock_imports):
        generate_autosummary_docs(genfiles, builder=app.builder,
                                  suffix=suffix, base_path=app.srcdir,
                                  app=app, imported_members=imported_members,
                                  overwrite=app.config.autosummary_generate_overwrite)
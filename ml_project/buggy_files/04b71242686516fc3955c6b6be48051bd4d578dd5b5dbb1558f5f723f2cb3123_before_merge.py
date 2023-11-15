def setup(app: "Sphinx") -> Dict[str, Any]:
    app.connect('config-inited', convert_source_suffix)
    app.connect('config-inited', init_numfig_format)
    app.connect('config-inited', correct_copyright_year)
    app.connect('config-inited', check_confval_types)
    app.connect('config-inited', check_primary_domain)
    app.connect('env-get-outdated', check_master_doc)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
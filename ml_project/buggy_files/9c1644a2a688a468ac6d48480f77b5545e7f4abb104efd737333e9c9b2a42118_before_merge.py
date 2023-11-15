def setup(app: Sphinx) -> Dict[str, Any]:
    app.setup_extension('sphinx.builders.latex.transforms')

    app.add_builder(LaTeXBuilder)
    app.connect('config-inited', validate_config_values)

    app.add_config_value('latex_engine', default_latex_engine, None,
                         ENUM('pdflatex', 'xelatex', 'lualatex', 'platex', 'uplatex'))
    app.add_config_value('latex_documents', default_latex_documents, None)
    app.add_config_value('latex_logo', None, None, [str])
    app.add_config_value('latex_appendices', [], None)
    app.add_config_value('latex_use_latex_multicolumn', False, None)
    app.add_config_value('latex_use_xindy', default_latex_use_xindy, None, [bool])
    app.add_config_value('latex_toplevel_sectioning', None, None,
                         ENUM(None, 'part', 'chapter', 'section'))
    app.add_config_value('latex_domain_indices', True, None, [list])
    app.add_config_value('latex_show_urls', 'no', None)
    app.add_config_value('latex_show_pagerefs', False, None)
    app.add_config_value('latex_elements', {}, None)
    app.add_config_value('latex_additional_files', [], None)
    app.add_config_value('latex_theme', 'manual', None, [str])
    app.add_config_value('latex_theme_path', [], None, [list])

    app.add_config_value('latex_docclass', default_latex_docclass, None)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
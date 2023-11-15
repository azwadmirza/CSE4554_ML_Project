def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(Epub3Builder)

    # config values
    app.add_config_value('epub_basename', lambda self: make_filename(self.project), None)
    app.add_config_value('epub_version', 3.0, 'epub')  # experimental
    app.add_config_value('epub_theme', 'epub', 'epub')
    app.add_config_value('epub_theme_options', {}, 'epub')
    app.add_config_value('epub_title', lambda self: self.project, 'epub')
    app.add_config_value('epub_author', lambda self: self.author, 'epub')
    app.add_config_value('epub_language', lambda self: self.language or 'en', 'epub')
    app.add_config_value('epub_publisher', lambda self: self.author, 'epub')
    app.add_config_value('epub_copyright', lambda self: self.copyright, 'epub')
    app.add_config_value('epub_identifier', 'unknown', 'epub')
    app.add_config_value('epub_scheme', 'unknown', 'epub')
    app.add_config_value('epub_uid', 'unknown', 'env')
    app.add_config_value('epub_cover', (), 'env')
    app.add_config_value('epub_guide', (), 'env')
    app.add_config_value('epub_pre_files', [], 'env')
    app.add_config_value('epub_post_files', [], 'env')
    app.add_config_value('epub_css_files', lambda config: config.html_css_files, 'epub')
    app.add_config_value('epub_exclude_files', [], 'env')
    app.add_config_value('epub_tocdepth', 3, 'env')
    app.add_config_value('epub_tocdup', True, 'env')
    app.add_config_value('epub_tocscope', 'default', 'env')
    app.add_config_value('epub_fix_images', False, 'env')
    app.add_config_value('epub_max_image_width', 0, 'env')
    app.add_config_value('epub_show_urls', 'inline', 'epub')
    app.add_config_value('epub_use_index', lambda self: self.html_use_index, 'epub')
    app.add_config_value('epub_description', 'unknown', 'epub')
    app.add_config_value('epub_contributor', 'unknown', 'epub')
    app.add_config_value('epub_writing_mode', 'horizontal', 'epub',
                         ENUM('horizontal', 'vertical'))

    # event handlers
    app.connect('config-inited', convert_epub_css_files)
    app.connect('builder-inited', validate_config_values)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
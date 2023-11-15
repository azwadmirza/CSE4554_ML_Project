def validate_config_values(app):
    if app.config.latex_toplevel_sectioning not in (None, 'part', 'chapter', 'section'):
        app.warn('invalid latex_toplevel_sectioning, ignored: %s' %
                 app.config.latex_toplevel_sectioning)
        app.config.latex_toplevel_sectioning = None

    if app.config.latex_use_parts:
        if app.config.latex_toplevel_sectioning:
            app.warn('latex_use_parts conflicts with latex_toplevel_sectioning, ignored.')
        else:
            app.warn('latex_use_parts is deprecated. Use latex_toplevel_sectioning instead.')
            app.config.latex_toplevel_sectioning = 'parts'

    if app.config.latex_use_modindex is not True:  # changed by user
        app.warn('latex_use_modindex is deprecated. Use latex_domain_indices instead.')

    if app.config.latex_preamble:
        if app.config.latex_elements.get('preamble'):
            app.warn("latex_preamble conflicts with latex_elements['preamble'], ignored.")
        else:
            app.warn("latex_preamble is deprecated. Use latex_elements['preamble'] instead.")
            app.config.latex_elements['preamble'] = app.config.latex_preamble

    if app.config.latex_paper_size != 'letter':
        if app.config.latex_elements.get('papersize'):
            app.warn("latex_paper_size conflicts with latex_elements['papersize'], ignored.")
        else:
            app.warn("latex_paper_size is deprecated. "
                     "Use latex_elements['papersize'] instead.")
            if app.config.latex_paper_size:
                app.config.latex_elements['papersize'] = app.config.latex_paper_size + 'paper'

    if app.config.latex_font_size != '10pt':
        if app.config.latex_elements.get('pointsize'):
            app.warn("latex_font_size conflicts with latex_elements['pointsize'], ignored.")
        else:
            app.warn("latex_font_size is deprecated. Use latex_elements['pointsize'] instead.")
            app.config.latex_elements['pointsize'] = app.config.latex_font_size

    if 'footer' in app.config.latex_elements:
        if 'postamble' in app.config.latex_elements:
            app.warn("latex_elements['footer'] conflicts with "
                     "latex_elements['postamble'], ignored.")
        else:
            app.warn("latex_elements['footer'] is deprecated. "
                     "Use latex_elements['preamble'] instead.")
            app.config.latex_elements['postamble'] = app.config.latex_elements['footer']
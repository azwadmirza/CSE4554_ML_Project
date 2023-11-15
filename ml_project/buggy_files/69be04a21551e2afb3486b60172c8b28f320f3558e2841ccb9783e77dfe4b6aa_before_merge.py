def display_figure(fig, message=None, max_width='100%'):
    "Display widgets applicable to the specified element"
    if OutputMagic.options['fig'] == 'repr': return None

    figure_format = OutputMagic.options['fig']
    dpi = OutputMagic.options['dpi']
    css = OutputMagic.options['css']
    backend = OutputMagic.options['backend']

    if backend == 'nbagg' and new_figure_manager_given_figure is not None:
        manager = new_figure_manager_given_figure(OutputMagic.nbagg_counter, fig)
        # Need to call mouse_init on each 3D axis to enable rotation support
        for ax in fig.get_axes():
            if isinstance(ax, Axes3D):
                ax.mouse_init()
        OutputMagic.nbagg_counter += 1
        manager.show()
        return ''
    elif backend == 'd3' and mpld3:
        fig.dpi = dpi
        mpld3.plugins.connect(fig, mpld3.plugins.MousePosition(fontsize=14))
        html = "<center>" + mpld3.fig_to_html(fig) + "<center/>"
    else:
        renderer = Store.renderer.instance(dpi=dpi)
        figdata = renderer.figure_data(fig, figure_format)
        if figure_format=='svg':
            figdata = figdata.encode("utf-8")
        b64 = base64.b64encode(figdata).decode("utf-8")
        (mime_type, tag) = MIME_TYPES[figure_format], HTML_TAGS[figure_format]
        src = HTML_TAGS['base64'].format(mime_type=mime_type, b64=b64)
        html = tag.format(src=src, css=dict_to_css(css))
    plt.close(fig)
    return html if (message is None) else '<b>%s</b></br>%s' % (message, html)
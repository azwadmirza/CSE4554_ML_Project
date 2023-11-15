def _plot_html(figure_or_data, config, validate, default_width,
               default_height, global_requirejs):
    # force no validation if frames is in the call
    # TODO - add validation for frames in call - #605
    if 'frames' in figure_or_data:
        figure = tools.return_figure_from_figure_or_data(
            figure_or_data, False
        )
    else:
        figure = tools.return_figure_from_figure_or_data(
            figure_or_data, validate
        )

    width = figure.get('layout', {}).get('width', default_width)
    height = figure.get('layout', {}).get('height', default_height)

    try:
        float(width)
    except (ValueError, TypeError):
        pass
    else:
        width = str(width) + 'px'

    try:
        float(height)
    except (ValueError, TypeError):
        pass
    else:
        height = str(height) + 'px'

    plotdivid = uuid.uuid4()
    jdata = json.dumps(figure.get('data', []), cls=utils.PlotlyJSONEncoder)
    jlayout = json.dumps(figure.get('layout', {}), cls=utils.PlotlyJSONEncoder)
    if 'frames' in figure_or_data:
        jframes = json.dumps(figure.get('frames', {}), cls=utils.PlotlyJSONEncoder)

    configkeys = (
        'editable',
        'autosizable',
        'fillFrame',
        'frameMargins',
        'scrollZoom',
        'doubleClick',
        'showTips',
        'showLink',
        'sendData',
        'linkText',
        'showSources',
        'displayModeBar',
        'modeBarButtonsToRemove',
        'modeBarButtonsToAdd',
        'modeBarButtons',
        'displaylogo',
        'plotGlPixelRatio',
        'setBackground',
        'topojsonURL'
    )

    config_clean = dict((k, config[k]) for k in configkeys if k in config)
    jconfig = json.dumps(config_clean)

    # TODO: The get_config 'source of truth' should
    # really be somewhere other than plotly.plotly
    plotly_platform_url = plotly.plotly.get_config().get('plotly_domain',
                                                         'https://plot.ly')
    if (plotly_platform_url != 'https://plot.ly' and
            config['linkText'] == 'Export to plot.ly'):

        link_domain = plotly_platform_url\
            .replace('https://', '')\
            .replace('http://', '')
        link_text = config['linkText'].replace('plot.ly', link_domain)
        config['linkText'] = link_text
        jconfig = jconfig.replace('Export to plot.ly', link_text)

    if 'frames' in figure_or_data:
        script = '''
        Plotly.plot(
            '{id}',
            {data},
            {layout},
            {config}
        ).then(function () {add_frames}).then(function(){animate})
        '''.format(
            id=plotdivid,
            data=jdata,
            layout=jlayout,
            config=jconfig,
            add_frames="{" + "return Plotly.addFrames('{id}',{frames}".format(
                id=plotdivid, frames=jframes
            ) + ");}",
            animate="{" + "Plotly.animate('{id}');".format(id=plotdivid) + "}"
        )
    else:
        script = 'Plotly.newPlot("{id}", {data}, {layout}, {config})'.format(
            id=plotdivid,
            data=jdata,
            layout=jlayout,
            config=jconfig)

    optional_line1 = ('require(["plotly"], function(Plotly) {{ '
                      if global_requirejs else '')
    optional_line2 = ('}});' if global_requirejs else '')

    plotly_html_div = (
        ''
        '<div id="{id}" style="height: {height}; width: {width};" '
        'class="plotly-graph-div">'
        '</div>'
        '<script type="text/javascript">' +
        optional_line1 +
        'window.PLOTLYENV=window.PLOTLYENV || {{}};'
        'window.PLOTLYENV.BASE_URL="' + plotly_platform_url + '";'
        '{script}' +
        optional_line2 +
        '</script>'
        '').format(
        id=plotdivid, script=script,
        height=height, width=width)

    return plotly_html_div, plotdivid, width, height
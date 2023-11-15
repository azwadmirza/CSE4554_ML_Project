def plot (data, pconfig={}):
    """ Plot a line graph with X,Y data.
    :param data: 2D dict, first keys as sample names, then x:y data pairs
    :param pconfig: optional dict with config key:value pairs. See CONTRIBUTING.md
    :return: HTML and JS, ready to be inserted into the page
    """

    # Given one dataset - turn it into a list
    if type(data) is not list:
        data = [data]

    # Smooth dataset if requested in config
    if pconfig.get('smooth_points', None) is not None:
        sumcounts = pconfig.get('smooth_points_sumcounts', True)
        for i, d in enumerate(data):
            sumc = sumcounts
            if type(sumcounts) is list:
                sumc = sumcounts[i]
            data[i] = smooth_line_data(d, pconfig['smooth_points'], sumc)

    # Generate the data dict structure expected by HighCharts series
    plotdata = list()
    for d in data:
        thisplotdata = list()
        for s in sorted(d.keys()):
            pairs = list()
            maxval = 0
            if 'categories' in pconfig:
                pconfig['categories'] = list()
                for k in d[s].keys():
                    pconfig['categories'].append(k)
                    pairs.append(d[s][k])
                    maxval = max(maxval, d[s][k])
            else:
                for k in sorted(d[s].keys()):
                    pairs.append([k, d[s][k]])
                    try:
                        maxval = max(maxval, d[s][k])
                    except TypeError:
                        pass
            if maxval > 0 or pconfig.get('hide_empty') is not True:
                this_series = { 'name': s, 'data': pairs }
                try:
                    this_series['color'] = pconfig['colors'][s]
                except: pass
                thisplotdata.append(this_series)
        plotdata.append(thisplotdata)

    # Add on annotation data series
    try:
        if pconfig.get('extra_series'):
            extra_series = pconfig['extra_series']
            if type(pconfig['extra_series']) == dict:
                extra_series = [[ pconfig['extra_series'] ]]
            elif type(pconfig['extra_series']) == list and type(pconfig['extra_series'][0]) == dict:
                extra_series = [ pconfig['extra_series'] ]
            for i, es in enumerate(extra_series):
                for s in es:
                    plotdata[i].append(s)
    except KeyError:
        pass

    # Make a plot - template custom, or interactive or flat
    try:
        return get_template_mod().linegraph(plotdata, pconfig)
    except (AttributeError, TypeError):
        if config.plots_force_flat or (not config.plots_force_interactive and len(plotdata[0]) > config.plots_flat_numseries):
            try:
                return matplotlib_linegraph(plotdata, pconfig)
            except:
                logger.error("############### Error making MatPlotLib figure! Falling back to HighCharts.")
                return highcharts_linegraph(plotdata, pconfig)
        else:
            # Use MatPlotLib to generate static plots if requested
            if config.export_plots:
                matplotlib_linegraph(plotdata, pconfig)
            # Return HTML for HighCharts dynamic plot
            return highcharts_linegraph(plotdata, pconfig)
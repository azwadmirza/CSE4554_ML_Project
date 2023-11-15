def plot (data, pconfig=None):
    """ Plot a line graph with X,Y data.
    :param data: 2D dict, first keys as sample names, then x:y data pairs
    :param pconfig: optional dict with config key:value pairs. See CONTRIBUTING.md
    :return: HTML and JS, ready to be inserted into the page
    """
    # Don't just use {} as the default argument as it's mutable. See:
    # http://python-guide-pt-br.readthedocs.io/en/latest/writing/gotchas/
    if pconfig is None:
        pconfig = {}

    # Allow user to overwrite any given config for this plot
    if 'id' in pconfig and pconfig['id'] and pconfig['id'] in config.custom_plot_config:
        for k, v in config.custom_plot_config[pconfig['id']].items():
            pconfig[k] = v

    # Given one dataset - turn it into a list
    if type(data) is not list:
        data = [data]

    # Validate config if linting
    if config.lint:
        # Get module name
        modname = ''
        callstack = inspect.stack()
        for n in callstack:
            if 'multiqc/modules/' in n[1] and 'base_module.py' not in n[1]:
                callpath = n[1].split('multiqc/modules/',1)[-1]
                modname = '>{}< '.format(callpath)
                break
        # Look for essential missing pconfig keys
        for k in ['id', 'title', 'ylab']:
            if k not in pconfig:
                errmsg = "LINT: {}Linegraph pconfig was missing key '{}'".format(modname, k)
                logger.error(errmsg)
                report.lint_errors.append(errmsg)
        # Check plot title format
        if not re.match( r'^[^:]*\S: \S[^:]*$', pconfig.get('title', '')):
            errmsg = "LINT: {} Linegraph title did not match format 'Module: Plot Name' (found '{}')".format(modname, pconfig.get('title', ''))
            logger.error(errmsg)
            report.lint_errors.append(errmsg)

    # Smooth dataset if requested in config
    if pconfig.get('smooth_points', None) is not None:
        sumcounts = pconfig.get('smooth_points_sumcounts', True)
        for i, d in enumerate(data):
            if type(sumcounts) is list:
                sumc = sumcounts[i]
            else:
                sumc = sumcounts
            data[i] = smooth_line_data(d, pconfig['smooth_points'], sumc)

    # Add sane plotting config defaults
    for idx, yp in enumerate(pconfig.get('yPlotLines', [])):
        pconfig['yPlotLines'][idx]["width"] = pconfig['yPlotLines'][idx].get("width", 2)

    # Add initial axis labels if defined in `data_labels` but not main config
    if pconfig.get('ylab') is None:
        try:
            pconfig['ylab'] = pconfig['data_labels'][0]['ylab']
        except (KeyError, IndexError):
            pass
    if pconfig.get('xlab') is None:
        try:
            pconfig['xlab'] = pconfig['data_labels'][0]['xlab']
        except (KeyError, IndexError):
            pass

    # Generate the data dict structure expected by HighCharts series
    plotdata = list()
    for data_index, d in enumerate(data):
        thisplotdata = list()

        for s in sorted(d.keys()):

            # Ensure any overwritting conditionals from data_labels (e.g. ymax) are taken in consideration
            series_config = pconfig.copy()
            if 'data_labels' in pconfig and type(pconfig['data_labels'][data_index]) is dict:  # if not a dict: only dataset name is provided
                series_config.update(pconfig['data_labels'][data_index])

            pairs = list()
            maxval = 0
            if 'categories' in series_config:
                pconfig['categories'] = list()
                for k in d[s].keys():
                    pconfig['categories'].append(k)
                    pairs.append(d[s][k])
                    maxval = max(maxval, d[s][k])
            else:
                for k in sorted(d[s].keys()):
                    if k is not None:
                        if 'xmax' in series_config and float(k) > float(series_config['xmax']):
                            continue
                        if 'xmin' in series_config and float(k) < float(series_config['xmin']):
                            continue
                    if d[s][k] is not None:
                        if 'ymax' in series_config and float(d[s][k]) > float(series_config['ymax']):
                            continue
                        if 'ymin' in series_config and float(d[s][k]) < float(series_config['ymin']):
                            continue
                    pairs.append([k, d[s][k]])
                    try:
                        maxval = max(maxval, d[s][k])
                    except TypeError:
                        pass
            if maxval > 0 or series_config.get('hide_empty') is not True:
                this_series = { 'name': s, 'data': pairs }
                try:
                    this_series['color'] = series_config['colors'][s]
                except:
                    pass
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
    except (KeyError, IndexError):
        pass

    # Make a plot - template custom, or interactive or flat
    try:
        return get_template_mod().linegraph(plotdata, pconfig)
    except (AttributeError, TypeError):
        if config.plots_force_flat or (not config.plots_force_interactive and len(plotdata[0]) > config.plots_flat_numseries):
            try:
                return matplotlib_linegraph(plotdata, pconfig)
            except Exception as e:
                logger.error("############### Error making MatPlotLib figure! Falling back to HighCharts.")
                logger.debug(e, exc_info=True)
                return highcharts_linegraph(plotdata, pconfig)
        else:
            # Use MatPlotLib to generate static plots if requested
            if config.export_plots:
                matplotlib_linegraph(plotdata, pconfig)
            # Return HTML for HighCharts dynamic plot
            return highcharts_linegraph(plotdata, pconfig)
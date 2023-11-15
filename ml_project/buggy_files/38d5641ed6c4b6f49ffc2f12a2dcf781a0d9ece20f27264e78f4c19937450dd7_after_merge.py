def get_forecast_component_plotly_props(m, fcst, name, uncertainty=True, plot_cap=False):
    """Prepares a dictionary for plotting the selected forecast component with Plotly

    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    name: Name of the component to plot.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.

    Returns
    -------
    A dictionary with Plotly traces, xaxis and yaxis
    """
    prediction_color = '#0072B2'
    error_color = 'rgba(0, 114, 178, 0.2)'  # '#0072B2' with 0.2 opacity
    cap_color = 'black'
    zeroline_color = '#AAA'
    line_width = 2

    range_margin = (fcst['ds'].max() - fcst['ds'].min()) * 0.05
    range_x = [fcst['ds'].min() - range_margin, fcst['ds'].max() + range_margin]

    text = None
    mode = 'lines'
    if name == 'holidays':
        
        # Combine holidays into one hover text
        holidays = m.construct_holiday_dataframe(fcst['ds'])
        holiday_features, _, _ = m.make_holiday_features(fcst['ds'], holidays)
        holiday_features.columns = holiday_features.columns.str.replace('_delim_', '', regex=False)
        holiday_features.columns = holiday_features.columns.str.replace('+0', '', regex=False)
        text = pd.Series(data='', index=holiday_features.index)
        for holiday_feature, idxs in holiday_features.iteritems():
            text[idxs.astype(bool) & (text != '')] += '<br>'  # Add newline if additional holiday
            text[idxs.astype(bool)] += holiday_feature

    traces = []
    traces.append(go.Scatter(
        name=name,
        x=fcst['ds'],
        y=fcst[name],
        mode=mode,
        line=go.scatter.Line(color=prediction_color, width=line_width),
        text=text,
    ))
    if uncertainty and m.uncertainty_samples and (fcst[name + '_upper'] != fcst[name + '_lower']).any():
        if mode == 'markers':
            traces[0].update(
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=fcst[name + '_upper'],
                    arrayminus=fcst[name + '_lower'],
                    width=0,
                    color=error_color
                )
            )
        else:
            traces.append(go.Scatter(
                name=name + '_upper',
                x=fcst['ds'],
                y=fcst[name + '_upper'],
                mode=mode,
                line=go.scatter.Line(width=0, color=error_color)
            ))
            traces.append(go.Scatter(
                name=name + '_lower',
                x=fcst['ds'],
                y=fcst[name + '_lower'],
                mode=mode,
                line=go.scatter.Line(width=0, color=error_color),
                fillcolor=error_color,
                fill='tonexty'
            ))
    if 'cap' in fcst and plot_cap:
        traces.append(go.Scatter(
            name='Cap',
            x=fcst['ds'],
            y=fcst['cap'],
            mode='lines',
            line=go.scatter.Line(color=cap_color, dash='dash', width=line_width),
        ))
    if m.logistic_floor and 'floor' in fcst and plot_cap:
        traces.append(go.Scatter(
            name='Floor',
            x=fcst['ds'],
            y=fcst['floor'],
            mode='lines',
            line=go.scatter.Line(color=cap_color, dash='dash', width=line_width),
        ))

    xaxis = go.layout.XAxis(
        type='date',
        range=range_x)
    yaxis = go.layout.YAxis(rangemode='normal' if name == 'trend' else 'tozero',
                            title=go.layout.yaxis.Title(text=name),
                            zerolinecolor=zeroline_color)
    if name in m.component_modes['multiplicative']:
        yaxis.update(tickformat='%', hoverformat='.2%')
    return {'traces': traces, 'xaxis': xaxis, 'yaxis': yaxis}
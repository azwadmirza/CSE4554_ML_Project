def resource_time_series(tasks, type='psutil_process_time_user', label='CPU user time'):
    tasks['epoch_time'] = (pd.to_datetime(
        tasks['timestamp']) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    step = int(tasks['resource_monitoring_interval'][0])
    start = tasks['epoch_time'].min()
    end = tasks['epoch_time'].max()
    tasks['relative_time'] = tasks['epoch_time'] - start
    bins = pd.cut(tasks['relative_time'], range(
        0, end - start + 1, step), include_lowest=True)

    df = tasks.groupby(bins, as_index=False)[type].mean()
    df['time'] = step * df.index
    fig = go.Figure(
        data=[go.Scatter(x=df['time'],
                         y=df[type],
                         )],
        layout=go.Layout(xaxis=dict(autorange=True,
                                    title='Time (seconds)'),
                         yaxis=dict(title=label),
                         title=label))
    return plot(fig, show_link=False, output_type="div", include_plotlyjs=False)
def _fake_click(fig, ax, point, xform='ax', button=1, kind='press'):
    """Helper to fake a click at a relative point within axes."""
    if xform == 'ax':
        x, y = ax.transAxes.transform_point(point)
    elif xform == 'data':
        x, y = ax.transData.transform_point(point)
    else:
        raise ValueError('unknown transform')
    if kind == 'press':
        func = partial(fig.canvas.button_press_event, x=x, y=y, button=button)
    elif kind == 'release':
        func = partial(fig.canvas.button_release_event, x=x, y=y,
                       button=button)
    elif kind == 'motion':
        func = partial(fig.canvas.motion_notify_event, x=x, y=y)
    try:
        func(guiEvent=None)
    except Exception:  # for old MPL
        func()
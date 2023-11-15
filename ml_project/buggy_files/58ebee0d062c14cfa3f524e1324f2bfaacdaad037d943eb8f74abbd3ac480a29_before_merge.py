def _fake_click(fig, ax, point, xform='ax', button=1):
    """Helper to fake a click at a relative point within axes."""
    if xform == 'ax':
        x, y = ax.transAxes.transform_point(point)
    elif xform == 'data':
        x, y = ax.transData.transform_point(point)
    else:
        raise ValueError('unknown transform')
    try:
        fig.canvas.button_press_event(x, y, button, False, None)
    except Exception:  # for old MPL
        fig.canvas.button_press_event(x, y, button, False)
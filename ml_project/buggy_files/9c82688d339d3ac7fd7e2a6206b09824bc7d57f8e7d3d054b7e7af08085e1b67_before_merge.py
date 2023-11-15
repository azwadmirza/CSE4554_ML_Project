def _plot_stc(stc, subject, surface, hemi, colormap, time_label,
              smoothing_steps, subjects_dir, views, clim, figure, initial_time,
              time_unit, background, time_viewer, colorbar, transparent,
              brain_alpha, overlay_alpha, vector_alpha, cortex, foreground,
              size, scale_factor, show_traces, src, volume_options,
              view_layout, add_data_kwargs):
    from .backends.renderer import _get_3d_backend
    from ..source_estimate import _BaseVolSourceEstimate
    vec = stc._data_ndim == 3
    subjects_dir = get_subjects_dir(subjects_dir=subjects_dir,
                                    raise_error=True)
    subject = _check_subject(stc.subject, subject, True)

    backend = _get_3d_backend()
    del _get_3d_backend
    using_mayavi = backend == "mayavi"
    if using_mayavi:
        from surfer import Brain
        _require_version('surfer', 'stc.plot', '0.9')
    else:  # PyVista
        from ._brain import Brain
    views = _check_views(surface, views, hemi, stc, backend)
    _check_option('hemi', hemi, ['lh', 'rh', 'split', 'both'])
    _check_option('view_layout', view_layout, ('vertical', 'horizontal'))
    time_label, times = _handle_time(time_label, time_unit, stc.times)

    # convert control points to locations in colormap
    use = stc.magnitude().data if vec else stc.data
    mapdata = _process_clim(clim, colormap, transparent, use,
                            allow_pos_lims=not vec)

    volume = _check_volume(stc, src, surface, backend)

    # XXX we should only need to do this for PySurfer/Mayavi, the PyVista
    # plotter should be smart enough to do this separation in the cmap-to-ctab
    # conversion. But this will need to be another refactoring that will
    # hopefully restore this line:
    #
    # if using_mayavi:
    _separate_map(mapdata)
    colormap = mapdata['colormap']
    diverging = 'pos_lims' in mapdata['clim']
    scale_pts = mapdata['clim']['pos_lims' if diverging else 'lims']
    transparent = mapdata['transparent']
    del mapdata

    if hemi in ['both', 'split']:
        hemis = ['lh', 'rh']
    else:
        hemis = [hemi]

    if overlay_alpha is None:
        overlay_alpha = brain_alpha
    if overlay_alpha == 0:
        smoothing_steps = 1  # Disable smoothing to save time.

    title = subject if len(hemis) > 1 else '%s - %s' % (subject, hemis[0])
    kwargs = {
        "subject_id": subject, "hemi": hemi, "surf": surface,
        "title": title, "cortex": cortex, "size": size,
        "background": background, "foreground": foreground,
        "figure": figure, "subjects_dir": subjects_dir,
        "views": views, "alpha": brain_alpha,
    }
    if backend in ['pyvista', 'notebook']:
        kwargs["show"] = False
        kwargs["view_layout"] = view_layout
    else:
        kwargs.update(_check_pysurfer_antialias(Brain))
        if view_layout != 'vertical':
            raise ValueError('view_layout must be "vertical" when using the '
                             'mayavi backend')
    with warnings.catch_warnings(record=True):  # traits warnings
        brain = Brain(**kwargs)
    del kwargs
    if scale_factor is None:
        # Configure the glyphs scale directly
        width = np.mean([np.ptp(brain.geo[hemi].coords[:, 1])
                         for hemi in hemis if hemi in brain.geo])
        scale_factor = 0.025 * width / scale_pts[-1]

    if transparent is None:
        transparent = True
    sd_kwargs = dict(transparent=transparent, verbose=False)
    center = 0. if diverging else None
    kwargs = {
        "array": stc,
        "colormap": colormap,
        "smoothing_steps": smoothing_steps,
        "time": times, "time_label": time_label,
        "alpha": overlay_alpha,
        "colorbar": colorbar,
        "vector_alpha": vector_alpha,
        "scale_factor": scale_factor,
        "verbose": False,
        "initial_time": initial_time,
        "transparent": transparent,
        "center": center,
        "fmin": scale_pts[0],
        "fmid": scale_pts[1],
        "fmax": scale_pts[2],
        "clim": clim,
        "src": src,
        "volume_options": volume_options,
        "verbose": False,
    }
    for hi, hemi in enumerate(hemis):
        if isinstance(stc, _BaseVolSourceEstimate):  # no surf data
            break
        vertices = stc.vertices[hi]
        if len(stc.vertices[hi]) == 0:  # no surf data for the given hemi
            continue  # no data
        use_kwargs = kwargs.copy()
        use_kwargs.update(hemi=hemi)
        if using_mayavi:
            del use_kwargs['clim'], use_kwargs['src']
            del use_kwargs['volume_options']
            use_kwargs.update(
                min=use_kwargs.pop('fmin'), mid=use_kwargs.pop('fmid'),
                max=use_kwargs.pop('fmax'), array=getattr(stc, hemi + '_data'),
                vertices=vertices)
        if add_data_kwargs is not None:
            use_kwargs.update(add_data_kwargs)
        with warnings.catch_warnings(record=True):  # traits warnings
            brain.add_data(**use_kwargs)
        if using_mayavi:
            brain.scale_data_colormap(fmin=scale_pts[0], fmid=scale_pts[1],
                                      fmax=scale_pts[2], **sd_kwargs)

    if volume:
        use_kwargs = kwargs.copy()
        use_kwargs.update(hemi='vol')
        brain.add_data(**use_kwargs)
    del kwargs

    need_peeling = (brain_alpha < 1.0 and
                    sys.platform != 'darwin' and
                    vec)
    if using_mayavi:
        for hemi in hemis:
            for b in brain._brain_list:
                for layer in b['brain'].data.values():
                    glyphs = layer['glyphs']
                    if glyphs is None:
                        continue
                    glyphs.glyph.glyph.scale_factor = scale_factor
                    glyphs.glyph.glyph.clamping = False
                    glyphs.glyph.glyph.range = (0., 1.)

        # depth peeling patch
        if need_peeling:
            for ff in brain._figures:
                for f in ff:
                    if f.scene is not None and sys.platform != 'darwin':
                        f.scene.renderer.use_depth_peeling = True
    elif need_peeling:
        brain.enable_depth_peeling()

    # time_viewer and show_traces
    _check_option('time_viewer', time_viewer, (True, False, 'auto'))
    _validate_type(show_traces, (str, bool, 'numeric'), 'show_traces')
    if isinstance(show_traces, str):
        _check_option('show_traces', show_traces, ('auto', 'separate'),
                      extra='when a string')
    if time_viewer == 'auto':
        time_viewer = not using_mayavi
    if show_traces == 'auto':
        show_traces = (
            not using_mayavi and
            time_viewer and
            brain._times is not None and
            len(brain._times) > 1
        )
    if show_traces and not time_viewer:
        raise ValueError('show_traces cannot be used when time_viewer=False')
    if using_mayavi and show_traces:
        raise NotImplementedError("show_traces=True is not available "
                                  "for the mayavi 3d backend.")
    if time_viewer:
        if using_mayavi:
            from surfer import TimeViewer
            TimeViewer(brain)
        else:  # PyVista
            brain.setup_time_viewer(time_viewer=time_viewer,
                                    show_traces=show_traces)
    else:
        if not using_mayavi:
            brain.show()

    return brain
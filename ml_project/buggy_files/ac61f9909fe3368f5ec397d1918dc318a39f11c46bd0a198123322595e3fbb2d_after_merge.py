def _plot_mpl_stc(stc, subject=None, surface='inflated', hemi='lh',
                  colormap='auto', time_label='auto', smoothing_steps=10,
                  subjects_dir=None, views='lat', clim='auto', figure=None,
                  initial_time=None, time_unit='s', background='black',
                  spacing='oct6', time_viewer=False, colorbar=True,
                  transparent=True):
    """Plot source estimate using mpl."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, analysis:ignore
    from matplotlib import cm
    from matplotlib.widgets import Slider
    import nibabel as nib
    from scipy import stats
    from ..morph import _get_subject_sphere_tris
    if hemi not in ['lh', 'rh']:
        raise ValueError("hemi must be 'lh' or 'rh' when using matplotlib. "
                         "Got %s." % hemi)
    lh_kwargs = {'lat': {'elev': 0, 'azim': 180},
                 'med': {'elev': 0, 'azim': 0},
                 'ros': {'elev': 0, 'azim': 90},
                 'cau': {'elev': 0, 'azim': -90},
                 'dor': {'elev': 90, 'azim': -90},
                 'ven': {'elev': -90, 'azim': -90},
                 'fro': {'elev': 0, 'azim': 106.739},
                 'par': {'elev': 30, 'azim': -120}}
    rh_kwargs = {'lat': {'elev': 0, 'azim': 0},
                 'med': {'elev': 0, 'azim': 180},
                 'ros': {'elev': 0, 'azim': 90},
                 'cau': {'elev': 0, 'azim': -90},
                 'dor': {'elev': 90, 'azim': -90},
                 'ven': {'elev': -90, 'azim': -90},
                 'fro': {'elev': 16.739, 'azim': 60},
                 'par': {'elev': 30, 'azim': -60}}
    time_viewer = False if time_viewer == 'auto' else time_viewer
    kwargs = dict(lh=lh_kwargs, rh=rh_kwargs)
    views = 'lat' if views == 'auto' else views
    _check_option('views', views, sorted(lh_kwargs.keys()))
    mapdata = _process_clim(clim, colormap, transparent, stc.data)
    _separate_map(mapdata)
    colormap, scale_pts = _linearize_map(mapdata)
    del transparent, mapdata

    time_label, times = _handle_time(time_label, time_unit, stc.times)
    fig = plt.figure(figsize=(6, 6)) if figure is None else figure
    ax = fig.gca(projection='3d')
    hemi_idx = 0 if hemi == 'lh' else 1
    surf = op.join(subjects_dir, subject, 'surf', '%s.%s' % (hemi, surface))
    if spacing == 'all':
        coords, faces = nib.freesurfer.read_geometry(surf)
        inuse = slice(None)
    else:
        stype, sval, ico_surf, src_type_str = _check_spacing(spacing)
        surf = _create_surf_spacing(surf, hemi, subject, stype, ico_surf,
                                    subjects_dir)
        inuse = surf['vertno']
        faces = surf['use_tris']
        coords = surf['rr'][inuse]
        shape = faces.shape
        faces = stats.rankdata(faces, 'dense').reshape(shape) - 1
        faces = np.round(faces).astype(int)  # should really be int-like anyway
    del surf
    vertices = stc.vertices[hemi_idx]
    n_verts = len(vertices)
    tris = _get_subject_sphere_tris(subject, subjects_dir)[hemi_idx]
    cmap = cm.get_cmap(colormap)
    greymap = cm.get_cmap('Greys')

    curv = nib.freesurfer.read_morph_data(
        op.join(subjects_dir, subject, 'surf', '%s.curv' % hemi))[inuse]
    curv = np.clip(np.array(curv > 0, np.int64), 0.33, 0.66)
    params = dict(ax=ax, stc=stc, coords=coords, faces=faces,
                  hemi_idx=hemi_idx, vertices=vertices, tris=tris,
                  smoothing_steps=smoothing_steps, n_verts=n_verts,
                  inuse=inuse, cmap=cmap, curv=curv,
                  scale_pts=scale_pts, greymap=greymap, time_label=time_label,
                  time_unit=time_unit)
    _smooth_plot(initial_time, params)

    ax.view_init(**kwargs[hemi][views])

    try:
        ax.set_facecolor(background)
    except AttributeError:
        ax.set_axis_bgcolor(background)

    if time_viewer:
        time_viewer = figure_nobar(figsize=(4.5, .25))
        fig.time_viewer = time_viewer
        ax_time = plt.axes()
        if initial_time is None:
            initial_time = 0
        slider = Slider(ax=ax_time, label='Time', valmin=times[0],
                        valmax=times[-1], valinit=initial_time)
        time_viewer.slider = slider
        callback_slider = partial(_smooth_plot, params=params)
        slider.on_changed(callback_slider)
        callback_key = partial(_key_pressed_slider, params=params)
        time_viewer.canvas.mpl_connect('key_press_event', callback_key)

        time_viewer.subplots_adjust(left=0.12, bottom=0.05, right=0.75,
                                    top=0.95)
    fig.subplots_adjust(left=0., bottom=0., right=1., top=1.)

    # add colorbar
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=plt.Normalize(scale_pts[0], scale_pts[2]))
    cax = inset_axes(ax, width="80%", height="5%", loc=8, borderpad=3.)
    plt.setp(plt.getp(cax, 'xticklabels'), color='w')
    sm.set_array(np.linspace(scale_pts[0], scale_pts[2], 256))
    if colorbar:
        cb = plt.colorbar(sm, cax=cax, orientation='horizontal')
        cb_yticks = plt.getp(cax, 'yticklabels')
        plt.setp(cb_yticks, color='w')
        cax.tick_params(labelsize=16)
        cb.patch.set_facecolor('0.5')
        cax.set(xlim=(scale_pts[0], scale_pts[2]))
    plt.show()
    return fig
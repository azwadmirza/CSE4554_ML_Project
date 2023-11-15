def plot_head_positions(pos, mode='traces', cmap='viridis', direction='z',
                        show=True, destination=None, info=None, color='k',
                        axes=None):
    """Plot head positions.

    Parameters
    ----------
    pos : ndarray, shape (n_pos, 10) | list of ndarray
        The head position data. Can also be a list to treat as a
        concatenation of runs.
    mode : str
        Can be 'traces' (default) to show position and quaternion traces,
        or 'field' to show the position as a vector field over time.
        The 'field' mode requires matplotlib 1.4+.
    cmap : colormap
        Colormap to use for the trace plot, default is "viridis".
    direction : str
        Can be any combination of "x", "y", or "z" (default: "z") to show
        directional axes in "field" mode.
    show : bool
        Show figure if True. Defaults to True.
    destination : str | array-like, shape (3,) | None
        The destination location for the head, assumed to be in head
        coordinates. See :func:`mne.preprocessing.maxwell_filter` for
        details.

        .. versionadded:: 0.16
    info : instance of mne.Info | None
        Measurement information. If provided, will be used to show the
        destination position when ``destination is None``, and for
        showing the MEG sensors.

        .. versionadded:: 0.16
    color : color object
        The color to use for lines in ``mode == 'traces'`` and quiver
        arrows in ``mode == 'field'``.

        .. versionadded:: 0.16
    axes : array-like, shape (3, 2)
        The matplotlib axes to use. Only used for ``mode == 'traces'``.

        .. versionadded:: 0.16

    Returns
    -------
    fig : instance of matplotlib.figure.Figure
        The figure.
    """
    from ..chpi import head_pos_to_trans_rot_t
    from ..preprocessing.maxwell import _check_destination
    import matplotlib.pyplot as plt
    _check_option('mode', mode, ['traces', 'field'])
    dest_info = dict(dev_head_t=None) if info is None else info
    destination = _check_destination(destination, dest_info, head_frame=True)
    if destination is not None:
        destination = _ensure_trans(destination, 'head', 'meg')  # probably inv
        destination = destination['trans'][:3].copy()
        destination[:, 3] *= 1000

    if not isinstance(pos, (list, tuple)):
        pos = [pos]
    for ii, p in enumerate(pos):
        p = np.array(p, float)
        if p.ndim != 2 or p.shape[1] != 10:
            raise ValueError('pos (or each entry in pos if a list) must be '
                             'dimension (N, 10), got %s' % (p.shape,))
        if ii > 0:  # concatenation
            p[:, 0] += pos[ii - 1][-1, 0] - p[0, 0]
        pos[ii] = p
    borders = np.cumsum([len(pp) for pp in pos])
    pos = np.concatenate(pos, axis=0)
    trans, rot, t = head_pos_to_trans_rot_t(pos)  # also ensures pos is okay
    # trans, rot, and t are for dev_head_t, but what we really want
    # is head_dev_t (i.e., where the head origin is in device coords)
    use_trans = einsum('ijk,ik->ij', rot[:, :3, :3].transpose([0, 2, 1]),
                       -trans) * 1000
    use_rot = rot.transpose([0, 2, 1])
    use_quats = -pos[:, 1:4]  # inverse (like doing rot.T)
    surf = rrs = lims = None
    if info is not None:
        meg_picks = pick_types(info, meg=True, ref_meg=False, exclude=())
        if len(meg_picks) > 0:
            rrs = 1000 * np.array([info['chs'][pick]['loc'][:3]
                                   for pick in meg_picks], float)
            if mode == 'traces':
                lims = np.array((rrs.min(0), rrs.max(0))).T
            else:  # mode == 'field'
                surf = get_meg_helmet_surf(info)
                transform_surface_to(surf, 'meg', info['dev_head_t'],
                                     copy=False)
                surf['rr'] *= 1000.
    helmet_color = (0.0, 0.0, 0.6)
    if mode == 'traces':
        if axes is None:
            axes = plt.subplots(3, 2, sharex=True)[1]
        else:
            axes = np.array(axes)
        if axes.shape != (3, 2):
            raise ValueError('axes must have shape (3, 2), got %s'
                             % (axes.shape,))
        fig = axes[0, 0].figure

        labels = ['xyz', ('$q_1$', '$q_2$', '$q_3$')]
        for ii, (quat, coord) in enumerate(zip(use_quats.T, use_trans.T)):
            axes[ii, 0].plot(t, coord, color, lw=1., zorder=3)
            axes[ii, 0].set(ylabel=labels[0][ii], xlim=t[[0, -1]])
            axes[ii, 1].plot(t, quat, color, lw=1., zorder=3)
            axes[ii, 1].set(ylabel=labels[1][ii], xlim=t[[0, -1]])
            for b in borders[:-1]:
                for jj in range(2):
                    axes[ii, jj].axvline(t[b], color='r')
        for ii, title in enumerate(('Position (mm)', 'Rotation (quat)')):
            axes[0, ii].set(title=title)
            axes[-1, ii].set(xlabel='Time (s)')
        if rrs is not None:
            pos_bads = np.any([(use_trans[:, ii] <= lims[ii, 0]) |
                               (use_trans[:, ii] >= lims[ii, 1])
                               for ii in range(3)], axis=0)
            for ii in range(3):
                oidx = list(range(ii)) + list(range(ii + 1, 3))
                # knowing it will generally be spherical, we can approximate
                # how far away we are along the axis line by taking the
                # point to the left and right with the smallest distance
                from scipy.spatial.distance import cdist
                dists = cdist(rrs[:, oidx], use_trans[:, oidx])
                left = rrs[:, [ii]] < use_trans[:, ii]
                left_dists_all = dists.copy()
                left_dists_all[~left] = np.inf
                # Don't show negative Z direction
                if ii != 2 and np.isfinite(left_dists_all).any():
                    idx = np.argmin(left_dists_all, axis=0)
                    left_dists = rrs[idx, ii]
                    bads = ~np.isfinite(
                        left_dists_all[idx, np.arange(len(idx))]) | pos_bads
                    left_dists[bads] = np.nan
                    axes[ii, 0].plot(t, left_dists, color=helmet_color,
                                     ls='-', lw=0.5, zorder=2)
                else:
                    axes[ii, 0].axhline(lims[ii][0], color=helmet_color,
                                        ls='-', lw=0.5, zorder=2)
                right_dists_all = dists
                right_dists_all[left] = np.inf
                if np.isfinite(right_dists_all).any():
                    idx = np.argmin(right_dists_all, axis=0)
                    right_dists = rrs[idx, ii]
                    bads = ~np.isfinite(
                        right_dists_all[idx, np.arange(len(idx))]) | pos_bads
                    right_dists[bads] = np.nan
                    axes[ii, 0].plot(t, right_dists, color=helmet_color,
                                     ls='-', lw=0.5, zorder=2)
                else:
                    axes[ii, 0].axhline(lims[ii][1], color=helmet_color,
                                        ls='-', lw=0.5, zorder=2)

        for ii in range(3):
            axes[ii, 1].set(ylim=[-1, 1])

        if destination is not None:
            vals = np.array([destination[:, 3],
                             rot_to_quat(destination[:, :3])]).T.ravel()
            for ax, val in zip(fig.axes, vals):
                ax.axhline(val, color='r', ls=':', zorder=2, lw=1.)

    else:  # mode == 'field':
        from matplotlib.colors import Normalize
        from mpl_toolkits.mplot3d.art3d import Line3DCollection
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, analysis:ignore
        fig, ax = plt.subplots(1, subplot_kw=dict(projection='3d'))

        # First plot the trajectory as a colormap:
        # http://matplotlib.org/examples/pylab_examples/multicolored_line.html
        pts = use_trans[:, np.newaxis]
        segments = np.concatenate([pts[:-1], pts[1:]], axis=1)
        norm = Normalize(t[0], t[-2])
        lc = Line3DCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(t[:-1])
        ax.add_collection(lc)
        # now plot the head directions as a quiver
        dir_idx = dict(x=0, y=1, z=2)
        kwargs = dict(pivot='tail')
        for d, length in zip(direction, [5., 2.5, 1.]):
            use_dir = use_rot[:, :, dir_idx[d]]
            # draws stems, then heads
            array = np.concatenate((t, np.repeat(t, 2)))
            ax.quiver(use_trans[:, 0], use_trans[:, 1], use_trans[:, 2],
                      use_dir[:, 0], use_dir[:, 1], use_dir[:, 2], norm=norm,
                      cmap=cmap, array=array, length=length, **kwargs)
            if destination is not None:
                ax.quiver(destination[0, 3],
                          destination[1, 3],
                          destination[2, 3],
                          destination[dir_idx[d], 0],
                          destination[dir_idx[d], 1],
                          destination[dir_idx[d], 2], color=color,
                          length=length, **kwargs)
        mins = use_trans.min(0)
        maxs = use_trans.max(0)
        if surf is not None:
            ax.plot_trisurf(*surf['rr'].T, triangles=surf['tris'],
                            color=helmet_color, alpha=0.1, shade=False)
            ax.scatter(*rrs.T, s=1, color=helmet_color)
            mins = np.minimum(mins, rrs.min(0))
            maxs = np.maximum(maxs, rrs.max(0))
        scale = (maxs - mins).max() / 2.
        xlim, ylim, zlim = (maxs + mins)[:, np.newaxis] / 2. + [-scale, scale]
        ax.set(xlabel='x', ylabel='y', zlabel='z',
               xlim=xlim, ylim=ylim, zlim=zlim)
        _set_aspect_equal(ax)
        ax.view_init(30, 45)
    tight_layout(fig=fig)
    plt_show(show)
    return fig
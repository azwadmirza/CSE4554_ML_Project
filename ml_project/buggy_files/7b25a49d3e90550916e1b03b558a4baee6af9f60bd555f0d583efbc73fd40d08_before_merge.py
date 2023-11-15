def paga_path(
    adata: AnnData,
    nodes: Sequence[Union[str, int]],
    keys: Sequence[str],
    use_raw: bool = True,
    annotations: Sequence[str] = ('dpt_pseudotime',),
    color_map: Union[str, Colormap, None] = None,
    color_maps_annotations: Mapping[str, Union[str, Colormap]] = MappingProxyType(
        dict(dpt_pseudotime='Greys')
    ),
    palette_groups: Optional[Sequence[str]] = None,
    n_avg: int = 1,
    groups_key: Optional[str] = None,
    xlim: Tuple[Optional[int], Optional[int]] = (None, None),
    title: Optional[str] = None,
    left_margin=None,
    ytick_fontsize: Optional[int] = None,
    title_fontsize: Optional[int] = None,
    show_node_names: bool = True,
    show_yticks: bool = True,
    show_colorbar: bool = True,
    legend_fontsize: Union[int, float, _FontSize, None] = None,
    legend_fontweight: Union[int, _FontWeight, None] = None,
    normalize_to_zero_one: bool = False,
    as_heatmap: bool = True,
    return_data: bool = False,
    show: Optional[bool] = None,
    save: Union[bool, str, None] = None,
    ax: Optional[Axes] = None,
) -> Optional[Axes]:
    """\
    Gene expression and annotation changes along paths in the abstracted graph.

    Parameters
    ----------
    adata
        An annotated data matrix.
    nodes
        A path through nodes of the abstracted graph, that is, names or indices
        (within `.categories`) of groups that have been used to run PAGA.
    keys
        Either variables in `adata.var_names` or annotations in
        `adata.obs`. They are plotted using `color_map`.
    use_raw
        Use `adata.raw` for retrieving gene expressions if it has been set.
    annotations
        Plot these keys with `color_maps_annotations`. Need to be keys for
        `adata.obs`.
    color_map
        Matplotlib colormap.
    color_maps_annotations
        Color maps for plotting the annotations. Keys of the dictionary must
        appear in `annotations`.
    palette_groups
        Ususally, use the same `sc.pl.palettes...` as used for coloring the
        abstracted graph.
    n_avg
        Number of data points to include in computation of running average.
    groups_key
        Key of the grouping used to run PAGA. If `None`, defaults to
        `adata.uns['paga']['groups']`.
    as_heatmap
        Plot the timeseries as heatmap. If not plotting as heatmap,
        `annotations` have no effect.
    show_node_names
        Plot the node names on the nodes bar.
    show_colorbar
        Show the colorbar.
    show_yticks
        Show the y ticks.
    normalize_to_zero_one
        Shift and scale the running average to [0, 1] per gene.
    return_data
        Return the timeseries data in addition to the axes if `True`.
    show
         Show the plot, do not return axis.
    save
        If `True` or a `str`, save the figure.
        A string is appended to the default filename.
        Infer the filetype if ending on \\{`'.pdf'`, `'.png'`, `'.svg'`\\}.
    ax
         A matplotlib axes object.

    Returns
    -------
    A :class:`~matplotlib.axes.Axes` object, if `ax` is `None`, else `None`.
    If `return_data`, return the timeseries data in addition to an axes.
    """
    ax_was_none = ax is None

    if groups_key is None:
        if 'groups' not in adata.uns['paga']:
            raise KeyError(
                'Pass the key of the grouping with which you ran PAGA, '
                'using the parameter `groups_key`.'
            )
        groups_key = adata.uns['paga']['groups']
    groups_names = adata.obs[groups_key].cat.categories

    if 'dpt_pseudotime' not in adata.obs.keys():
        raise ValueError(
            '`pl.paga_path` requires computation of a pseudotime `tl.dpt` '
            'for ordering at single-cell resolution'
        )

    if palette_groups is None:
        _utils.add_colors_for_categorical_sample_annotation(adata, groups_key)
        palette_groups = adata.uns[f'{groups_key}_colors']

    def moving_average(a):
        return _sc_utils.moving_average(a, n_avg)

    ax = pl.gca() if ax is None else ax

    X = []
    x_tick_locs = [0]
    x_tick_labels = []
    groups = []
    anno_dict = {anno: [] for anno in annotations}
    if isinstance(nodes[0], str):
        nodes_ints = []
        groups_names_set = set(groups_names)
        for node in nodes:
            if node not in groups_names_set:
                raise ValueError(
                    f'Each node/group needs to be in {groups_names.tolist()} '
                    f'(`groups_key`={groups_key!r}) not {node!r}.'
                )
            nodes_ints.append(groups_names.get_loc(node))
        nodes_strs = nodes
    else:
        nodes_ints = nodes
        nodes_strs = [groups_names[node] for node in nodes]

    adata_X = adata
    if use_raw and adata.raw is not None:
        adata_X = adata.raw

    for ikey, key in enumerate(keys):
        x = []
        for igroup, group in enumerate(nodes_ints):
            idcs = np.arange(adata.n_obs)[
                adata.obs[groups_key].values == nodes_strs[igroup]
            ]
            if len(idcs) == 0:
                raise ValueError(
                    'Did not find data points that match '
                    f'`adata.obs[{groups_key!r}].values == {str(group)!r}`. '
                    f'Check whether `adata.obs[{groups_key!r}]` '
                    'actually contains what you expect.'
                )
            idcs_group = np.argsort(
                adata.obs['dpt_pseudotime'].values[
                    adata.obs[groups_key].values == nodes_strs[igroup]
                ]
            )
            idcs = idcs[idcs_group]
            if key in adata.obs_keys():
                x += list(adata.obs[key].values[idcs])
            else:
                x += list(adata_X[:, key].X[idcs])
            if ikey == 0:
                groups += [group for i in range(len(idcs))]
                x_tick_locs.append(len(x))
                for anno in annotations:
                    series = adata.obs[anno]
                    if is_categorical_dtype(series):
                        series = series.cat.codes
                    anno_dict[anno] += list(series.values[idcs])
        if n_avg > 1:
            x = moving_average(x)
            if ikey == 0:
                for key in annotations:
                    if not isinstance(anno_dict[key][0], str):
                        anno_dict[key] = moving_average(anno_dict[key])
        if normalize_to_zero_one:
            x -= np.min(x)
            x /= np.max(x)
        X.append(x)
        if not as_heatmap:
            ax.plot(x[xlim[0] : xlim[1]], label=key)
        if ikey == 0:
            for igroup, group in enumerate(nodes):
                if len(groups_names) > 0 and group not in groups_names:
                    label = groups_names[group]
                else:
                    label = group
                x_tick_labels.append(label)
    X = np.array(X)
    if as_heatmap:
        img = ax.imshow(X, aspect='auto', interpolation='nearest', cmap=color_map)
        if show_yticks:
            ax.set_yticks(range(len(X)))
            ax.set_yticklabels(keys, fontsize=ytick_fontsize)
        else:
            ax.set_yticks([])
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.tick_params(axis='both', which='both', length=0)
        ax.grid(False)
        if show_colorbar:
            pl.colorbar(img, ax=ax)
        left_margin = 0.2 if left_margin is None else left_margin
        pl.subplots_adjust(left=left_margin)
    else:
        left_margin = 0.4 if left_margin is None else left_margin
        if len(keys) > 1:
            pl.legend(
                frameon=False,
                loc='center left',
                bbox_to_anchor=(-left_margin, 0.5),
                fontsize=legend_fontsize,
            )
    xlabel = groups_key
    if not as_heatmap:
        ax.set_xlabel(xlabel)
        pl.yticks([])
        if len(keys) == 1:
            pl.ylabel(keys[0] + ' (a.u.)')
    else:
        import matplotlib.colors

        # groups bar
        ax_bounds = ax.get_position().bounds
        groups_axis = pl.axes(
            (
                ax_bounds[0],
                ax_bounds[1] - ax_bounds[3] / len(keys),
                ax_bounds[2],
                ax_bounds[3] / len(keys),
            )
        )
        groups = np.array(groups)[None, :]
        groups_axis.imshow(
            groups,
            aspect='auto',
            interpolation="nearest",
            cmap=matplotlib.colors.ListedColormap(
                # the following line doesn't work because of normalization
                # adata.uns['paga_groups_colors'])
                palette_groups[np.min(groups).astype(int) :],
                N=int(np.max(groups) + 1 - np.min(groups)),
            ),
        )
        if show_yticks:
            groups_axis.set_yticklabels(['', xlabel, ''], fontsize=ytick_fontsize)
        else:
            groups_axis.set_yticks([])
        groups_axis.set_frame_on(False)
        if show_node_names:
            ypos = (groups_axis.get_ylim()[1] + groups_axis.get_ylim()[0]) / 2
            x_tick_locs = _sc_utils.moving_average(x_tick_locs, n=2)
            for ilabel, label in enumerate(x_tick_labels):
                groups_axis.text(
                    x_tick_locs[ilabel],
                    ypos,
                    x_tick_labels[ilabel],
                    fontdict=dict(
                        horizontalalignment='center',
                        verticalalignment='center',
                    ),
                )
        groups_axis.set_xticks([])
        groups_axis.grid(False)
        groups_axis.tick_params(axis='both', which='both', length=0)
        # further annotations
        y_shift = ax_bounds[3] / len(keys)
        for ianno, anno in enumerate(annotations):
            if ianno > 0:
                y_shift = ax_bounds[3] / len(keys) / 2
            anno_axis = pl.axes(
                (
                    ax_bounds[0],
                    ax_bounds[1] - (ianno + 2) * y_shift,
                    ax_bounds[2],
                    y_shift,
                )
            )
            arr = np.array(anno_dict[anno])[None, :]
            if anno not in color_maps_annotations:
                color_map_anno = (
                    'Vega10' if is_categorical_dtype(adata.obs[anno]) else 'Greys'
                )
            else:
                color_map_anno = color_maps_annotations[anno]
            img = anno_axis.imshow(
                arr,
                aspect='auto',
                interpolation='nearest',
                cmap=color_map_anno,
            )
            if show_yticks:
                anno_axis.set_yticklabels(['', anno, ''], fontsize=ytick_fontsize)
                anno_axis.tick_params(axis='both', which='both', length=0)
            else:
                anno_axis.set_yticks([])
            anno_axis.set_frame_on(False)
            anno_axis.set_xticks([])
            anno_axis.grid(False)
    if title is not None:
        ax.set_title(title, fontsize=title_fontsize)
    if show is None and not ax_was_none:
        show = False
    else:
        show = settings.autoshow if show is None else show
    _utils.savefig_or_show('paga_path', show=show, save=save)
    if return_data:
        df = pd.DataFrame(data=X.T, columns=keys)
        df['groups'] = moving_average(groups)  # groups is without moving average, yet
        if 'dpt_pseudotime' in anno_dict:
            df['distance'] = anno_dict['dpt_pseudotime'].T
        return ax, df if ax_was_none and not show else df
    else:
        return ax if ax_was_none and not show else None
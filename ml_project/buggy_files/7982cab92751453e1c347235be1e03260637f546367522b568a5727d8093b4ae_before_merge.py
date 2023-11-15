def restrict_forward_to_stc(fwd, stc):
    """Restrict forward operator to active sources in a source estimate.

    Parameters
    ----------
    fwd : Forward
        Forward operator.
    stc : SourceEstimate
        Source estimate.

    Returns
    -------
    fwd_out : dict
        Restricted forward operator.

    See Also
    --------
    restrict_forward_to_label
    """
    fwd_out = deepcopy(fwd)
    src_sel = _stc_src_sel(fwd['src'], stc)

    fwd_out['source_rr'] = fwd['source_rr'][src_sel]
    fwd_out['nsource'] = len(src_sel)

    if is_fixed_orient(fwd):
        idx = src_sel
    else:
        idx = (3 * src_sel[:, None] + np.arange(3)).ravel()

    fwd_out['source_nn'] = fwd['source_nn'][idx]
    fwd_out['sol']['data'] = fwd['sol']['data'][:, idx]
    fwd_out['sol']['ncol'] = len(idx)

    for i in range(2):
        fwd_out['src'][i]['vertno'] = stc.vertices[i]
        fwd_out['src'][i]['nuse'] = len(stc.vertices[i])
        fwd_out['src'][i]['inuse'] = fwd['src'][i]['inuse'].copy()
        fwd_out['src'][i]['inuse'].fill(0)
        fwd_out['src'][i]['inuse'][stc.vertices[i]] = 1
        fwd_out['src'][i]['use_tris'] = np.array([], int)
        fwd_out['src'][i]['nuse_tri'] = np.array([0])

    return fwd_out
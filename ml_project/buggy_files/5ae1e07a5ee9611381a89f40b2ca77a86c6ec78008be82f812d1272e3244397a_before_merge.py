def restrict_forward_to_label(fwd, labels):
    """Restrict forward operator to labels.

    Parameters
    ----------
    fwd : Forward
        Forward operator.
    labels : label object | list
        Label object or list of label objects.

    Returns
    -------
    fwd_out : dict
        Restricted forward operator.

    See Also
    --------
    restrict_forward_to_stc
    """
    message = 'labels must be instance of Label or a list of Label.'
    vertices = [np.array([], int), np.array([], int)]

    if not isinstance(labels, list):
        labels = [labels]

    # Get vertices separately of each hemisphere from all label
    for label in labels:
        if not isinstance(label, Label):
            raise TypeError(message + ' Instead received %s' % type(label))
        i = 0 if label.hemi == 'lh' else 1
        vertices[i] = np.append(vertices[i], label.vertices)
    # Remove duplicates and sort
    vertices = [np.unique(vert_hemi) for vert_hemi in vertices]

    fwd_out = deepcopy(fwd)
    fwd_out['source_rr'] = np.zeros((0, 3))
    fwd_out['nsource'] = 0
    fwd_out['source_nn'] = np.zeros((0, 3))
    fwd_out['sol']['data'] = np.zeros((fwd['sol']['data'].shape[0], 0))
    fwd_out['sol']['ncol'] = 0
    nuse_lh = fwd['src'][0]['nuse']

    for i in range(2):
        fwd_out['src'][i]['vertno'] = np.array([], int)
        fwd_out['src'][i]['nuse'] = 0
        fwd_out['src'][i]['inuse'] = fwd['src'][i]['inuse'].copy()
        fwd_out['src'][i]['inuse'].fill(0)
        fwd_out['src'][i]['use_tris'] = np.array([], int)
        fwd_out['src'][i]['nuse_tri'] = np.array([0])

        # src_sel is idx to cols in fwd that are in any label per hemi
        src_sel = np.intersect1d(fwd['src'][i]['vertno'], vertices[i])
        src_sel = np.searchsorted(fwd['src'][i]['vertno'], src_sel)

        # Reconstruct each src
        vertno = fwd['src'][i]['vertno'][src_sel]
        fwd_out['src'][i]['inuse'][vertno] = 1
        fwd_out['src'][i]['nuse'] += len(vertno)
        fwd_out['src'][i]['vertno'] = np.where(fwd_out['src'][i]['inuse'])[0]

        # Reconstruct part of fwd that is not sol data
        src_sel += i * nuse_lh  # Add column shift to right hemi
        fwd_out['source_rr'] = np.vstack([fwd_out['source_rr'],
                                          fwd['source_rr'][src_sel]])
        fwd_out['nsource'] += len(src_sel)

        if is_fixed_orient(fwd):
            idx = src_sel
        else:
            idx = (3 * src_sel[:, None] + np.arange(3)).ravel()

        fwd_out['source_nn'] = np.vstack([fwd_out['source_nn'],
                                          fwd['source_nn'][idx]])
        fwd_out['sol']['data'] = np.hstack([fwd_out['sol']['data'],
                                            fwd['sol']['data'][:, idx]])
        fwd_out['sol']['ncol'] += len(idx)

    return fwd_out
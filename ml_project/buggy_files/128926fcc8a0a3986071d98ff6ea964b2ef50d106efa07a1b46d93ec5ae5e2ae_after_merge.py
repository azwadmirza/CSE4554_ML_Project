def revert_actions(prefix, revision=-1, index=None):
    # TODO: If revision raise a revision error, should always go back to a safe revision
    # change
    h = History(prefix)
    user_requested_specs = itervalues(h.get_requested_specs_map())
    try:
        state = h.get_state(revision)
    except IndexError:
        raise CondaIndexError("no such revision: %d" % revision)

    curr = h.get_state()
    if state == curr:
        return UnlinkLinkTransaction()

    _supplement_index_with_prefix(index, prefix)
    r = Resolve(index)

    state = r.dependency_sort({d.name: d for d in (Dist(s) for s in state)})
    curr = set(Dist(s) for s in curr)

    link_dists = tuple(d for d in state if not is_linked(prefix, d))
    unlink_dists = set(curr) - set(state)

    # check whether it is a safe revision
    for dist in concatv(link_dists, unlink_dists):
        if dist not in index:
            from .exceptions import CondaRevisionError
            msg = "Cannot revert to {}, since {} is not in repodata".format(revision, dist)
            raise CondaRevisionError(msg)

    unlink_precs = tuple(index[d] for d in unlink_dists)
    link_precs = tuple(index[d] for d in link_dists)
    stp = PrefixSetup(prefix, unlink_precs, link_precs, (), user_requested_specs)
    txn = UnlinkLinkTransaction(stp)
    return txn
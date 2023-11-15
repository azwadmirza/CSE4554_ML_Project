def combine_install_requirements(ireqs):
    """
    Return a single install requirement that reflects a combination of
    all the inputs.
    """
    # We will store the source ireqs in a _source_ireqs attribute;
    # if any of the inputs have this, then use those sources directly.
    source_ireqs = []
    for ireq in ireqs:
        source_ireqs.extend(getattr(ireq, "_source_ireqs", [ireq]))
    source_ireqs.sort(key=str)

    # deepcopy the accumulator so as to not modify the inputs
    combined_ireq = copy.deepcopy(source_ireqs[0])
    for ireq in source_ireqs[1:]:
        # NOTE we may be losing some info on dropped reqs here
        combined_ireq.req.specifier &= ireq.req.specifier
        combined_ireq.constraint &= ireq.constraint
        # Return a sorted, de-duped tuple of extras
        combined_ireq.extras = tuple(
            sorted(set(tuple(combined_ireq.extras) + tuple(ireq.extras)))
        )

    # InstallRequirements objects are assumed to come from only one source, and
    # so they support only a single comes_from entry. This function breaks this
    # model. As a workaround, we deterministically choose a single source for
    # the comes_from entry, and add an extra _source_ireqs attribute to keep
    # track of multiple sources for use within pip-tools.
    if len(source_ireqs) > 1:
        if any(ireq.comes_from is None for ireq in source_ireqs):
            # None indicates package was directly specified.
            combined_ireq.comes_from = None
        else:
            # Populate the comes_from field from one of the sources.
            # Requirement input order is not stable, so we need to sort:
            # We choose the shortest entry in order to keep the printed
            # representation as concise as possible.
            combined_ireq.comes_from = min(
                (ireq.comes_from for ireq in source_ireqs),
                key=lambda x: (len(str(x)), str(x)),
            )
        combined_ireq._source_ireqs = source_ireqs
    return combined_ireq
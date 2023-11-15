def valve_flowreorder(input_ofmsgs, use_barriers=True):
    """Reorder flows for better OFA performance."""
    # Move all deletes to be first, and add one barrier,
    # while optionally randomizing order. Platforms that do
    # parallel delete will perform better and platforms that
    # don't will have at most only one barrier to deal with.
    output_ofmsgs = []
    by_kind = _partition_ofmsgs(input_ofmsgs)

    # Suppress all other deletes if a global delete is present.
    delete_global_ofmsgs = by_kind.get('deleteglobal', [])
    if delete_global_ofmsgs:
        by_kind['delete'] = []

    for kind, random_order, suggest_barrier in _OFMSG_ORDER:
        ofmsgs = dedupe_ofmsgs(by_kind.get(kind, []), random_order)
        if ofmsgs:
            output_ofmsgs.extend(ofmsgs)
            if use_barriers and suggest_barrier:
                output_ofmsgs.append(barrier())
    return output_ofmsgs
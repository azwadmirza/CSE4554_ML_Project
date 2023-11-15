def valve_flowreorder(input_ofmsgs, use_barriers=True):
    """Reorder flows for better OFA performance."""
    # Move all deletes to be first, and add one barrier,
    # while optionally randomizing order. Platforms that do
    # parallel delete will perform better and platforms that
    # don't will have at most only one barrier to deal with.
    output_ofmsgs = []
    by_kind = _partition_ofmsgs(input_ofmsgs)

    # Suppress all other relevant deletes if a global delete is present.
    delete_global_ofmsgs = by_kind.get('deleteglobal', [])
    if delete_global_ofmsgs:
        global_types = []
        for ofmsg in delete_global_ofmsgs:
            global_types.append(type(ofmsg))
        new_delete = []
        for ofmsg in by_kind.get('delete', []):
            if type(ofmsg) not in global_types:
                new_delete.append(ofmsg)
        by_kind['delete'] = new_delete

    for kind, random_order, suggest_barrier in _OFMSG_ORDER:
        ofmsgs = dedupe_ofmsgs(by_kind.get(kind, []), random_order)
        if ofmsgs:
            output_ofmsgs.extend(ofmsgs)
            if use_barriers and suggest_barrier:
                output_ofmsgs.append(barrier())
    return output_ofmsgs
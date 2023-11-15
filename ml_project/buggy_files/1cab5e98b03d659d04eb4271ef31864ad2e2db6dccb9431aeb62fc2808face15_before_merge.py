def form_blocks(data, axes):
    # pre-filter out items if we passed it
    items = axes[0]

    if len(data) < len(items):
        extra_items = items - Index(data.keys())
    else:
        extra_items = []

    # put "leftover" items in float bucket, where else?
    # generalize?
    float_dict = {}
    int_dict = {}
    bool_dict = {}
    object_dict = {}
    for k, v in data.iteritems():
        if issubclass(v.dtype.type, np.floating):
            float_dict[k] = v
        elif issubclass(v.dtype.type, np.integer):
            int_dict[k] = v
        elif v.dtype == np.bool_:
            bool_dict[k] = v
        else:
            object_dict[k] = v

    blocks = []
    if len(float_dict):
        float_block = _simple_blockify(float_dict, items, np.float64)
        blocks.append(float_block)

    if len(int_dict):
        int_block = _simple_blockify(int_dict, items, np.int64)
        blocks.append(int_block)

    if len(bool_dict):
        bool_block = _simple_blockify(bool_dict, items, np.bool_)
        blocks.append(bool_block)

    if len(object_dict) > 0:
        object_block = _simple_blockify(object_dict, items, np.object_)
        blocks.append(object_block)

    if len(extra_items):
        shape = (len(extra_items),) + tuple(len(x) for x in axes[1:])
        block_values = np.empty(shape, dtype=float)
        block_values.fill(nan)

        na_block = make_block(block_values, extra_items, items,
                              do_integrity_check=True)
        blocks.append(na_block)
        blocks = _consolidate(blocks, items)

    return blocks
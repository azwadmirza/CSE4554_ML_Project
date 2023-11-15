def make_block(values, items, ref_items, do_integrity_check=False):
    dtype = values.dtype
    vtype = dtype.type

    if issubclass(vtype, np.floating):
        klass = FloatBlock
    elif issubclass(vtype, np.integer):
        if vtype != np.int64:
            values = values.astype('i8')
        klass = IntBlock
    elif dtype == np.bool_:
        klass = BoolBlock
    else:
        klass = ObjectBlock

    return klass(values, items, ref_items, ndim=values.ndim,
                 do_integrity_check=do_integrity_check)
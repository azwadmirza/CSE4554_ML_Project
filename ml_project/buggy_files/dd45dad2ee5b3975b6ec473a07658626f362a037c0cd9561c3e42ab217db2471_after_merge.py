def _get_incref_decref(context, module, datamodel, container_type):
    assert datamodel.contains_nrt_meminfo()

    fe_type = datamodel.fe_type
    data_ptr_ty = datamodel.get_data_type().as_pointer()
    refct_fnty = ir.FunctionType(ir.VoidType(), [data_ptr_ty])
    incref_fn = module.get_or_insert_function(
        refct_fnty,
        name='.numba_{}_incref${}'.format(container_type, fe_type),
    )

    builder = ir.IRBuilder(incref_fn.append_basic_block())
    context.nrt.incref(
        builder, fe_type,
        datamodel.load_from_data_pointer(builder, incref_fn.args[0]),
    )
    builder.ret_void()

    decref_fn = module.get_or_insert_function(
        refct_fnty,
        name='.numba_{}_decref${}'.format(container_type, fe_type),
    )
    builder = ir.IRBuilder(decref_fn.append_basic_block())
    context.nrt.decref(
        builder, fe_type,
        datamodel.load_from_data_pointer(builder, decref_fn.args[0]),
    )
    builder.ret_void()

    return incref_fn, decref_fn
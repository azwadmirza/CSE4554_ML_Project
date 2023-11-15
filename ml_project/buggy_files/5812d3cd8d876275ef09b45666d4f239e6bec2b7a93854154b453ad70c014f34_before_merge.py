def set_cuda_kernel(lfunc):
    from llvmlite.llvmpy.core import MetaData, MetaDataString, Constant, Type

    m = lfunc.module

    ops = lfunc, MetaDataString.get(m, "kernel"), Constant.int(Type.int(), 1)
    md = MetaData.get(m, ops)

    nmd = m.get_or_insert_named_metadata('nvvm.annotations')
    nmd.add(md)

    # Set NVVM IR version
    i32 = ir.IntType(32)
    if NVVM().is_nvvm70:
        # NVVM IR 1.6, DWARF 3.0
        ir_versions = [i32(1), i32(6), i32(3), i32(0)]
    else:
        # NVVM IR 1.1, DWARF 2.0
        ir_versions = [i32(1), i32(2), i32(2), i32(0)]

    md_ver = m.add_metadata(ir_versions)
    m.add_named_metadata('nvvmir.version', md_ver)
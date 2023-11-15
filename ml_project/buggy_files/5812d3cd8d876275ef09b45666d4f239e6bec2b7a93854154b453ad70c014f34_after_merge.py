def set_cuda_kernel(lfunc):
    from llvmlite.llvmpy.core import MetaData, MetaDataString, Constant, Type

    mod = lfunc.module

    ops = lfunc, MetaDataString.get(mod, "kernel"), Constant.int(Type.int(), 1)
    md = MetaData.get(mod, ops)

    nmd = mod.get_or_insert_named_metadata('nvvm.annotations')
    nmd.add(md)
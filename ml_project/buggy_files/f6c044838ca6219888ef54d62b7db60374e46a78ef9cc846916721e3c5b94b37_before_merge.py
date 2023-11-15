def jit(func_or_sig=None, device=False, debug=False, argtypes=None,
        inline=False, restype=None, fastmath=False, link=None):
    if link is not None:
        raise NotImplementedError('Cannot link PTX in the simulator')
    # Check for first argument specifying types - in that case the
    # decorator is not being passed a function
    if func_or_sig is None or isinstance(func_or_sig, (str, tuple, Signature)):
        def jitwrapper(fn):
            return FakeCUDAKernel(fn,
                                  device=device,
                                  fastmath=fastmath)
        return jitwrapper
    return FakeCUDAKernel(func_or_sig, device=device)
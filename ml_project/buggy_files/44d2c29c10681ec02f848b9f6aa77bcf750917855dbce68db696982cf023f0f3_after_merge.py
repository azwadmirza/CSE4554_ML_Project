def compile_cuda(pyfunc, return_type, args, debug=False, inline=False):
    from .descriptor import cuda_target
    typingctx = cuda_target.typingctx
    targetctx = cuda_target.targetctx

    flags = compiler.Flags()
    # Do not compile (generate native code), just lower (to LLVM)
    flags.set('no_compile')
    flags.set('no_cpython_wrapper')
    flags.set('no_cfunc_wrapper')
    if debug:
        flags.set('debuginfo')
    if inline:
        flags.set('forceinline')
    # Run compilation pipeline
    cres = compiler.compile_extra(typingctx=typingctx,
                                  targetctx=targetctx,
                                  func=pyfunc,
                                  args=args,
                                  return_type=return_type,
                                  flags=flags,
                                  locals={})

    library = cres.library
    library.finalize()

    return cres
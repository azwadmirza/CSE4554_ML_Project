def module_extension_sources(file, use_cython, no_cuda):
    pyx, others = ensure_module_file(file)
    base = path.join(*pyx.split('.'))
    if use_cython:
        pyx = base + '.pyx'
        if not os.path.exists(pyx):
            use_cython = False
            print(
                'NOTICE: Skipping cythonize as {} does not exist.'.format(pyx))
    if not use_cython:
        pyx = base + '.cpp'

    # If CUDA SDK is not available, remove CUDA C files from extension sources
    # and use stubs defined in header files.
    if no_cuda:
        others1 = []
        for source in others:
            base, ext = os.path.splitext(source)
            if ext == '.cu':
                continue
            others1.append(source)
        others = others1

    return [pyx] + others
def _compile_with_cache_cuda(
        source, options, arch, cache_dir, extra_source=None, backend='nvrtc',
        enable_cooperative_groups=False, name_expressions=None,
        log_stream=None, cache_in_memory=False, jitify=False):
    # NVRTC does not use extra_source. extra_source is used for cache key.
    global _empty_file_preprocess_cache
    if cache_dir is None:
        cache_dir = get_cache_dir()
    if arch is None:
        arch = _get_arch()

    options += ('-ftz=true',)

    if enable_cooperative_groups:
        # `cooperative_groups` requires `-rdc=true`.
        # The three latter flags are to resolve linker error.
        # (https://devtalk.nvidia.com/default/topic/1023604/linker-error/)
        options += ('-rdc=true', '-Xcompiler', '-fPIC', '-shared')

    if _get_bool_env_variable('CUPY_CUDA_COMPILE_WITH_DEBUG', False):
        options += ('--device-debug', '--generate-line-info')

    is_jitify_requested = ('-DCUPY_USE_JITIFY' in options)
    if jitify and not is_jitify_requested:
        # jitify is set in RawKernel/RawModule, translate it to an option
        # that is useless to the compiler, but can be used as part of the
        # hash key
        options += ('-DCUPY_USE_JITIFY',)
    elif is_jitify_requested and not jitify:
        # jitify is requested internally, just set the flag
        jitify = True
    if jitify and backend != 'nvrtc':
        raise ValueError('jitify only works with NVRTC')

    env = (arch, options, _get_nvrtc_version(), backend)
    base = _empty_file_preprocess_cache.get(env, None)
    if base is None:
        # This is checking of NVRTC compiler internal version
        base = _preprocess('', options, arch, backend)
        _empty_file_preprocess_cache[env] = base

    key_src = '%s %s %s %s' % (env, base, source, extra_source)
    key_src = key_src.encode('utf-8')
    name = '%s_2.cubin' % hashlib.md5(key_src).hexdigest()

    mod = function.Module()

    if not cache_in_memory:
        # Read from disk cache
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        # To handle conflicts in concurrent situation, we adopt lock-free
        # method to avoid performance degradation.
        # We force recompiling to retrieve C++ mangled names if so desired.
        path = os.path.join(cache_dir, name)
        if os.path.exists(path) and not name_expressions:
            with open(path, 'rb') as file:
                data = file.read()
            if len(data) >= 32:
                hash = data[:32]
                cubin = data[32:]
                cubin_hash = hashlib.md5(cubin).hexdigest().encode('ascii')
                if hash == cubin_hash:
                    mod.load(cubin)
                    return mod
    else:
        # Enforce compiling -- the resulting kernel will be cached elsewhere,
        # so we do nothing
        pass

    if backend == 'nvrtc':
        cu_name = '' if cache_in_memory else name + '.cu'
        ptx, mapping = compile_using_nvrtc(
            source, options, arch, cu_name, name_expressions,
            log_stream, cache_in_memory, jitify)
        if _is_cudadevrt_needed(options):
            # for separate compilation
            ls = function.LinkState()
            ls.add_ptr_data(ptx, 'cupy.ptx')
            _cudadevrt = _get_cudadevrt_path()
            ls.add_ptr_file(_cudadevrt)
            cubin = ls.complete()
        else:
            cubin = ptx
        mod._set_mapping(mapping)
    elif backend == 'nvcc':
        rdc = _is_cudadevrt_needed(options)
        cubin = compile_using_nvcc(source, options, arch,
                                   name + '.cu', code_type='cubin',
                                   separate_compilation=rdc,
                                   log_stream=log_stream)
    else:
        raise ValueError('Invalid backend %s' % backend)

    if not cache_in_memory:
        # Write to disk cache
        cubin_hash = hashlib.md5(cubin).hexdigest().encode('ascii')

        # shutil.move is not atomic operation, so it could result in a
        # corrupted file. We detect it by appending md5 hash at the beginning
        # of each cache file. If the file is corrupted, it will be ignored
        # next time it is read.
        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False) as tf:
            tf.write(cubin_hash)
            tf.write(cubin)
            temp_path = tf.name
        shutil.move(temp_path, path)

        # Save .cu source file along with .cubin
        if _get_bool_env_variable('CUPY_CACHE_SAVE_CUDA_SOURCE', False):
            with open(path + '.cu', 'w') as f:
                f.write(source)
    else:
        # we don't do any disk I/O
        pass

    mod.load(cubin)
    return mod
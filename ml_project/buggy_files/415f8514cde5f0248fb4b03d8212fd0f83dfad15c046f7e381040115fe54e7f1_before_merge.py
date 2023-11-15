def build_mx_extension(build_ext, options):
    # clear ROLE -- installation does not need this
    os.environ.pop("DMLC_ROLE", None)

    check_mx_version()
    mx_compile_flags, mx_link_flags = get_mx_flags(
        build_ext, options['COMPILE_FLAGS'])

    mx_have_cuda = is_mx_cuda()
    macro_have_cuda = check_macro(options['MACROS'], 'HAVE_CUDA')
    if not mx_have_cuda and macro_have_cuda:
        raise DistutilsPlatformError(
            'BytePS build with GPU support was requested, but this MXNet '
            'installation does not support CUDA.')

    # Update HAVE_CUDA to mean that MXNet supports CUDA.
    if mx_have_cuda and not macro_have_cuda:
        cuda_include_dirs, cuda_lib_dirs = get_cuda_dirs(
            build_ext, options['COMPILE_FLAGS'])
        options['MACROS'] += [('HAVE_CUDA', '1')]
        options['INCLUDES'] += cuda_include_dirs
        options['LIBRARY_DIRS'] += cuda_lib_dirs
        options['LIBRARIES'] += ['cudart']

    mxnet_lib.define_macros = options['MACROS']
    if check_macro(options['MACROS'], 'HAVE_CUDA'):
        mxnet_lib.define_macros += [('MSHADOW_USE_CUDA', '1')]
    else:
        mxnet_lib.define_macros += [('MSHADOW_USE_CUDA', '0')]
    mxnet_lib.define_macros += [('MSHADOW_USE_MKL', '0')]

    # use MXNet's DMLC headers first instead of ps-lite's
    options['INCLUDES'].insert(0, get_mx_include_dirs())
    mxnet_lib.include_dirs = options['INCLUDES']
    mxnet_lib.sources = options['SOURCES'] + \
        ['byteps/mxnet/ops.cc',
         'byteps/mxnet/ready_event.cc',
         'byteps/mxnet/tensor_util.cc',
         'byteps/mxnet/cuda_util.cc',
         'byteps/mxnet/adapter.cc']
    mxnet_lib.extra_compile_args = options['COMPILE_FLAGS'] + \
        mx_compile_flags
    mxnet_lib.extra_link_args = options['LINK_FLAGS'] + mx_link_flags
    mxnet_lib.extra_objects = options['EXTRA_OBJECTS']
    mxnet_lib.library_dirs = options['LIBRARY_DIRS']
    mxnet_lib.libraries = options['LIBRARIES']

    build_ext.build_extension(mxnet_lib)
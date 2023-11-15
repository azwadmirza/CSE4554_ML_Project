def get_mx_flags(build_ext, cpp_flags):
    mx_include_dirs = [get_mx_include_dirs()]
    mx_lib_dirs = get_mx_lib_dirs()
    mx_libs = get_mx_libs(build_ext, mx_lib_dirs, cpp_flags)

    compile_flags = []
    has_mkldnn = is_mx_mkldnn()
    for include_dir in mx_include_dirs:
        compile_flags.append('-I%s' % include_dir)
        if has_mkldnn:
            mkldnn_include = os.path.join(include_dir, 'mkldnn')
            compile_flags.append('-I%s' % mkldnn_include)

    link_flags = []
    for lib_dir in mx_lib_dirs:
        link_flags.append('-Wl,-rpath,%s' % lib_dir)
        link_flags.append('-L%s' % lib_dir)

    for lib in mx_libs:
        link_flags.append('-l%s' % lib)

    return compile_flags, link_flags
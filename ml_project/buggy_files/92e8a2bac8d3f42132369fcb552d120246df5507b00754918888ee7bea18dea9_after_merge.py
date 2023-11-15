def find_matching_gcc_compiler_path(gxx_compiler_version):
    for path_dir, bin_file in enumerate_binaries_in_path():
        if re.match('^gcc(?:-\\d+(?:\\.\\d+)*)?$', bin_file):
            # gcc, or gcc-7, gcc-4.9, or gcc-4.8.5
            compiler = os.path.join(path_dir, bin_file)
            compiler_version = determine_gcc_version(compiler)
            if compiler_version and compiler_version == gxx_compiler_version:
                return compiler

    print('INFO: Unable to find gcc compiler (version %s).' % gxx_compiler_version)
    return None
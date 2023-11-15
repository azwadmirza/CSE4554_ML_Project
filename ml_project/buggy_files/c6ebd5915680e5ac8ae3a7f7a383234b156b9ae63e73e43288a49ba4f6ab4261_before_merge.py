def configuration(parent_package="", top_path=None):
    """
    Config function mainly used to compile C and Fortran code.
    """
    config = Configuration("", parent_package, top_path)

    # GSE2
    path = os.path.join(SETUP_DIRECTORY, "obspy", "gse2", "src", "GSE_UTI")
    files = [os.path.join(path, "gse_functions.c")]
    # compiler specific options
    kwargs = {}
    if IS_MSVC:
        # get export symbols
        kwargs['export_symbols'] = export_symbols(path, 'gse_functions.def')
    config.add_extension(_get_lib_name("gse2", during_build=True), files,
                         **kwargs)

    # LIBMSEED
    path = os.path.join(SETUP_DIRECTORY, "obspy", "mseed", "src")
    files = glob.glob(os.path.join(path, "libmseed", "*.c"))
    files.append(os.path.join(path, "obspy-readbuffer.c"))
    # compiler specific options
    kwargs = {}
    if IS_MSVC:
        # needed by libmseed lmplatform.h
        kwargs['define_macros'] = [('WIN32', '1')]
        # get export symbols
        kwargs['export_symbols'] = \
            export_symbols(path, 'libmseed', 'libmseed.def')
        kwargs['export_symbols'] += \
            export_symbols(path, 'obspy-readbuffer.def')
        # workaround Win32 and MSVC - see issue #64
        if '32' in platform.architecture()[0]:
            kwargs['extra_compile_args'] = ["/fp:strict"]
    config.add_extension(_get_lib_name("mseed", during_build=True), files,
                         **kwargs)

    # SEGY
    path = os.path.join(SETUP_DIRECTORY, "obspy", "segy", "src")
    files = [os.path.join(path, "ibm2ieee.c")]
    # compiler specific options
    kwargs = {}
    if IS_MSVC:
        # get export symbols
        kwargs['export_symbols'] = export_symbols(path, 'libsegy.def')
    config.add_extension(_get_lib_name("segy", during_build=True), files,
                         **kwargs)

    # SIGNAL
    path = os.path.join(SETUP_DIRECTORY, "obspy", "signal", "src")
    files = glob.glob(os.path.join(path, "*.c"))
    # compiler specific options
    kwargs = {}
    if IS_MSVC:
        # get export symbols
        kwargs['export_symbols'] = export_symbols(path, 'libsignal.def')
    config.add_extension(_get_lib_name("signal", during_build=True), files,
                         **kwargs)

    # EVALRESP
    path = os.path.join(SETUP_DIRECTORY, "obspy", "signal", "src")
    files = glob.glob(os.path.join(path, "evalresp", "*.c"))
    # compiler specific options
    kwargs = {}
    if IS_MSVC:
        # needed by evalresp evresp.h
        kwargs['define_macros'] = [('WIN32', '1')]
        # get export symbols
        kwargs['export_symbols'] = export_symbols(path, 'libevresp.def')
    config.add_extension(_get_lib_name("evresp", during_build=True), files,
                         **kwargs)

    # TAUP
    path = os.path.join(SETUP_DIRECTORY, "obspy", "taup", "src")
    libname = _get_lib_name("tau", during_build=True)
    files = glob.glob(os.path.join(path, "*.f"))
    # compiler specific options
    kwargs = {'libraries': []}
    # XXX: The build subdirectory is difficult to determine if installed
    # via pypi or other means. I could not find a reliable way of doing it.
    new_interface_path = os.path.join("build", libname + os.extsep + "pyf")
    interface_file = os.path.join(path, "_libtau.pyf")
    with open(interface_file, "r") as open_file:
        interface_file = open_file.read()
    # In the original .pyf file the library is called _libtau.
    interface_file = interface_file.replace("_libtau", libname)
    if not os.path.exists("build"):
        os.mkdir("build")
    with open(new_interface_path, "w") as open_file:
        open_file.write(interface_file)
    files.insert(0, new_interface_path)
    # we do not need this when linking with gcc, only when linking with
    # gfortran the option -lgcov is required
    if os.environ.get('OBSPY_C_COVERAGE', ""):
        kwargs['libraries'].append('gcov')
    config.add_extension(libname, files, **kwargs)

    add_data_files(config)

    return config
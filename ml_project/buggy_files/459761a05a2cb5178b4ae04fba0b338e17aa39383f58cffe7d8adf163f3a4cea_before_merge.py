def load_ldconfig_cache():
    """
    Create a cache of the `ldconfig`-output to call it only once.
    It contains thousands of libraries and running it on every dylib
    is expensive.
    """
    global LDCONFIG_CACHE

    if LDCONFIG_CACHE is not None:
        return

    from distutils.spawn import find_executable
    ldconfig = find_executable('ldconfig')
    if ldconfig is None:
        # If `lsconfig` is not found in $PATH, search it in some fixed
        # directories. Simply use a second call instead of fiddling
        # around with checks for empty env-vars and string-concat.
        ldconfig = find_executable('ldconfig',
                                   '/usr/sbin:/sbin:/usr/bin:/usr/sbin')

        # if we still couldn't find 'ldconfig' command
        if ldconfig is None:
            LDCONFIG_CACHE = {}
            return

    if is_freebsd or is_openbsd:
        # This has a quite different format than other Unixes
        # [vagrant@freebsd-10 ~]$ ldconfig -r
        # /var/run/ld-elf.so.hints:
        #     search directories: /lib:/usr/lib:/usr/lib/compat:...
        #     0:-lgeom.5 => /lib/libgeom.so.5
        #   184:-lpython2.7.1 => /usr/local/lib/libpython2.7.so.1
        ldconfig_arg = '-r'
        splitlines_count = 2
        pattern = re.compile(r'^\s+\d+:-l(\S+)(\s.*)? => (\S+)')
    else:
        # Skip first line of the library list because it is just
        # an informative line and might contain localized characters.
        # Example of first line with local cs_CZ.UTF-8:
        #$ /sbin/ldconfig -p
        #V keši „/etc/ld.so.cache“ nalezeno knihoven: 2799
        #      libzvbi.so.0 (libc6,x86-64) => /lib64/libzvbi.so.0
        #      libzvbi-chains.so.0 (libc6,x86-64) => /lib64/libzvbi-chains.so.0
        ldconfig_arg = '-p'
        splitlines_count = 1
        pattern = re.compile(r'^\s+(\S+)(\s.*)? => (\S+)')

    try:
        text = compat.exec_command(ldconfig, ldconfig_arg)
    except ExecCommandFailed:
        logger.warning("Failed to execute ldconfig. Disabling LD cache.")
        LDCONFIG_CACHE = {}
        return

    text = text.strip().splitlines()[splitlines_count:]

    LDCONFIG_CACHE = {}
    for line in text:
        # :fixme: this assumes libary names do not contain whitespace
        m = pattern.match(line)
        path = m.groups()[-1]
        if is_freebsd or is_openbsd:
            # Insert `.so` at the end of the lib's basename. soname
            # and filename may have (different) trailing versions. We
            # assume the `.so` in the filename to mark the end of the
            # lib's basename.
            bname = os.path.basename(path).split('.so', 1)[0]
            name = 'lib' + m.group(1)
            assert name.startswith(bname)
            name = bname + '.so' + name[len(bname):]
        else:
            name = m.group(1)
        # ldconfig may know about several versions of the same lib,
        # e.g. differents arch, different libc, etc. Use the first
        # entry.
        if not name in LDCONFIG_CACHE:
            LDCONFIG_CACHE[name] = path
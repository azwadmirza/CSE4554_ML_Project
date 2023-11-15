    def install(self, spec, prefix):
        env['GEOS_DIR'] = spec['geos'].prefix
        setup_py('install', '--prefix=%s' % prefix)

        # We are not sure if this fix is needed before Python 3.5.2.
        # If it is needed, this test should be changed.
        # See: https://github.com/LLNL/spack/pull/1964
        if spec['python'].version >= Version('3.5.2'):
            # Use symlinks to join the two mpl_toolkits/ directories into
            # one, inside of basemap.  This is because Basemap tries to
            # "add to" an existing package in Matplotlib, which is only
            # legal Python for "Implicit Namespace Packages":
            #     https://www.python.org/dev/peps/pep-0420/
            #     https://github.com/Homebrew/homebrew-python/issues/112
            # In practice, Python will see only the basemap version of
            # mpl_toolkits
            path_m = find_package_dir(
                spec['py-matplotlib'].prefix, 'mpl_toolkits')
            path_b = find_package_dir(spec.prefix, 'mpl_toolkits')
            link_dir(path_m, path_b)
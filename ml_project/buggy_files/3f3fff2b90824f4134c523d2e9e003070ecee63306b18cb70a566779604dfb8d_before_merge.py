    def __enter__(self):
        self.save_path = os.environ.get('PATH', None)
        self.save_pythonpath = os.environ.get('PYTHONPATH', None)
        self.save_nousersite = os.environ.get('PYTHONNOUSERSITE', None)

        install_scheme = 'nt' if (os.name == 'nt') else 'posix_prefix'
        install_dirs = get_paths(install_scheme, vars={
            'base': self.path,
            'platbase': self.path,
        })

        scripts = install_dirs['scripts']
        if self.save_path:
            os.environ['PATH'] = scripts + os.pathsep + self.save_path
        else:
            os.environ['PATH'] = scripts + os.pathsep + os.defpath

        # Note: prefer distutils' sysconfig to get the
        # library paths so PyPy is correctly supported.
        purelib = get_python_lib(plat_specific=0, prefix=self.path)
        platlib = get_python_lib(plat_specific=1, prefix=self.path)
        if purelib == platlib:
            lib_dirs = purelib
        else:
            lib_dirs = purelib + os.pathsep + platlib
        if self.save_pythonpath:
            os.environ['PYTHONPATH'] = lib_dirs + os.pathsep + \
                self.save_pythonpath
        else:
            os.environ['PYTHONPATH'] = lib_dirs

        os.environ['PYTHONNOUSERSITE'] = '1'

        return self.path
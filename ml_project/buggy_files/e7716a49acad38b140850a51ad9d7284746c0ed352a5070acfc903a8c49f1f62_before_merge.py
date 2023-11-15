    def create_kernel_spec(self):
        """Create a kernel spec for our own kernels"""
        # Paths that we need to add to PYTHONPATH:
        # 1. sc_path: Path to our sitecustomize
        # 2. spy_path: Path to our main module, so we can use our config
        #    system to configure kernels started by exterrnal interpreters
        # 3. spy_pythonpath: Paths saved by our users with our PYTHONPATH
        #    manager
        spy_path = get_module_source_path('spyder')
        sc_path = osp.join(spy_path, 'utils', 'site')
        spy_pythonpath = self.main.get_spyder_pythonpath()

        default_interpreter = CONF.get('main_interpreter', 'default')
        if default_interpreter:
            pathlist = [sc_path] + spy_pythonpath
        else:
            pathlist = [sc_path, spy_path] + spy_pythonpath
        pypath = add_pathlist_to_PYTHONPATH([], pathlist, ipyconsole=True,
                                            drop_env=(not default_interpreter))

        # Python interpreter used to start kernels
        if default_interpreter:
            pyexec = get_python_executable()
        else:
            # Avoid IPython adding the virtualenv on which Spyder is running
            # to the kernel sys.path
            os.environ.pop('VIRTUAL_ENV', None)
            pyexec = CONF.get('main_interpreter', 'executable')

        # Fixes Issue #3427
        if os.name == 'nt':
            dir_pyexec = osp.dirname(pyexec)
            pyexec_w = osp.join(dir_pyexec, 'pythonw.exe')
            if osp.isfile(pyexec_w):
                pyexec = pyexec_w

        # Command used to start kernels
        utils_path = osp.join(spy_path, 'utils', 'ipython')
        kernel_cmd = [
            pyexec,
            osp.join("%s" % utils_path, "start_kernel.py"),
            '-f',
            '{connection_file}'
        ]

        # Environment variables that we need to pass to our sitecustomize
        umr_namelist = CONF.get('main_interpreter', 'umr/namelist')

        if PY2:
            original_list = umr_namelist[:]
            for umr_n in umr_namelist:
                try:
                    umr_n.encode('utf-8')
                except UnicodeDecodeError:
                    umr_namelist.remove(umr_n)
            if original_list != umr_namelist:
                CONF.set('main_interpreter', 'umr/namelist', umr_namelist)

        env_vars = {
            'IPYTHON_KERNEL': 'True',
            'EXTERNAL_INTERPRETER': not default_interpreter,
            'UMR_ENABLED': CONF.get('main_interpreter', 'umr/enabled'),
            'UMR_VERBOSE': CONF.get('main_interpreter', 'umr/verbose'),
            'UMR_NAMELIST': ','.join(umr_namelist)
        }

        # Add our PYTHONPATH to env_vars
        env_vars.update(pypath)

        # Making all env_vars strings
        for k,v in iteritems(env_vars):
            if PY2:
                uv = to_text_string(v)
                env_vars[k] = to_binary_string(uv, encoding='utf-8')
            else:
                env_vars[k] = to_text_string(v)

        # Dict for our kernel spec
        kernel_dict = {
            'argv': kernel_cmd,
            'display_name': 'Spyder',
            'language': 'python',
            'env': env_vars
        }

        return KernelSpec(resource_dir='', **kernel_dict)
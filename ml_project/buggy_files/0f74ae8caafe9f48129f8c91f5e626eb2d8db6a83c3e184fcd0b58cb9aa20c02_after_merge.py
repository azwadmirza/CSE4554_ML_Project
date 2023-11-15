    def argv(self):
        """Command to start kernels"""
        # Python interpreter used to start kernels
        if CONF.get('main_interpreter', 'default'):
            pyexec = get_python_executable()
        else:
            # Avoid IPython adding the virtualenv on which Spyder is running
            # to the kernel sys.path
            os.environ.pop('VIRTUAL_ENV', None)
            pyexec = CONF.get('main_interpreter', 'executable')
            if not is_python_interpreter(pyexec):
                pyexec = get_python_executable()
                CONF.set('main_interpreter', 'executable', '')
                CONF.set('main_interpreter', 'default', True)
                CONF.set('main_interpreter', 'custom', False)

        # Part of spyder-ide/spyder#11819
        is_different = is_different_interpreter(pyexec)

        # Command used to start kernels
        if is_different and is_conda_env(pyexec=pyexec):
            # If this is a conda environment we need to call an intermediate
            # activation script to correctly activate the spyder-kernel

            # If changes are needed on this section make sure you also update
            # the activation scripts at spyder/plugins/ipythonconsole/scripts/
            kernel_cmd = [
                get_activation_script(),  # This is bundled with Spyder
                get_conda_activation_script(),
                get_conda_env_path(pyexec),  # Might be external
                pyexec,
                '{connection_file}',
            ]
        else:
            kernel_cmd = [
                pyexec,
                '-m',
                'spyder_kernels.console',
                '-f',
                '{connection_file}'
            ]
        logger.info('Kernel command: {}'.format(kernel_cmd))

        return kernel_cmd
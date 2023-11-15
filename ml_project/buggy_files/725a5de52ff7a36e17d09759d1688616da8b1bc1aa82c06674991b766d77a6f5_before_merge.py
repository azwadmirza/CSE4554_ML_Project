    def run(self):
        from distutils.version import StrictVersion
        if StrictVersion(setuptools.__version__) < StrictVersion('9.1'):
            sys.stderr.write(
                '\n\nInstalling Salt requires setuptools >= 9.1\n'
                'Available setuptools version is {}\n\n'.format(setuptools.__version__)
            )
            sys.stderr.flush()
            sys.exit(1)

        # Let's set the running_salt_install attribute so we can add
        # _version.py in the build command
        self.distribution.running_salt_install = True
        self.distribution.salt_version_hardcoded_path = os.path.join(
            self.build_lib, 'salt', '_version.py'
        )
        if IS_WINDOWS_PLATFORM:
            # Download the required DLLs
            self.distribution.salt_download_windows_dlls = True
            self.run_command('download-windows-dlls')
            self.distribution.salt_download_windows_dlls = None
        # Run install.run
        install.run(self)
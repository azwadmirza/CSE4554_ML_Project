    def finalize_install(self, install_requests):
        self.atomic_dir.finalize()

        # The install_chroot is keyed by the hash of the wheel file (zip) we installed. Here we add a
        # key by the hash of the exploded wheel dir (the install_chroot). This latter key is used by
        # zipped PEXes at runtime to explode their wheel chroots to the filesystem. By adding the key
        # here we short-circuit the explode process for PEXes created and run on the same machine.
        #
        # From a clean cache after building a simple pex this looks like:
        # $ rm -rf ~/.pex
        # $ python -mpex -c pex -o /tmp/pex.pex .
        # $ tree -L 4 ~/.pex/
        # /home/jsirois/.pex/
        # ├── built_wheels
        # │   └── 1003685de2c3604dc6daab9540a66201c1d1f718
        # │       └── cp-38-cp38
        # │           └── pex-2.0.2-py2.py3-none-any.whl
        # └── installed_wheels
        #     ├── 2a594cef34d2e9109bad847358d57ac4615f81f4
        #     │   └── pex-2.0.2-py2.py3-none-any.whl
        #     │       ├── bin
        #     │       ├── pex
        #     │       └── pex-2.0.2.dist-info
        #     └── ae13cba3a8e50262f4d730699a11a5b79536e3e1
        #         └── pex-2.0.2-py2.py3-none-any.whl -> /home/jsirois/.pex/installed_wheels/2a594cef34d2e9109bad847358d57ac4615f81f4/pex-2.0.2-py2.py3-none-any.whl  # noqa
        #
        # 11 directories, 1 file
        #
        # And we see in the created pex, the runtime key that the layout above satisfies:
        # $ unzip -qc /tmp/pex.pex PEX-INFO | jq .distributions
        # {
        #   "pex-2.0.2-py2.py3-none-any.whl": "ae13cba3a8e50262f4d730699a11a5b79536e3e1"
        # }
        #
        # When the pex is run, the runtime key is followed to the build time key, avoiding re-unpacking
        # the wheel:
        # $ PEX_VERBOSE=1 /tmp/pex.pex --version
        # pex: Found site-library: /usr/lib/python3.8/site-packages
        # pex: Tainted path element: /usr/lib/python3.8/site-packages
        # pex: Scrubbing from user site: /home/jsirois/.local/lib/python3.8/site-packages
        # pex: Scrubbing from site-packages: /usr/lib/python3.8/site-packages
        # pex: Activating PEX virtual environment from /tmp/pex.pex: 9.1ms
        # pex: Bootstrap complete, performing final sys.path modifications...
        # pex: PYTHONPATH contains:
        # pex:     /tmp/pex.pex
        # pex:   * /usr/lib/python38.zip
        # pex:     /usr/lib/python3.8
        # pex:     /usr/lib/python3.8/lib-dynload
        # pex:     /home/jsirois/.pex/installed_wheels/2a594cef34d2e9109bad847358d57ac4615f81f4/pex-2.0.2-py2.py3-none-any.whl  # noqa
        # pex:   * /tmp/pex.pex/.bootstrap
        # pex:   * - paths that do not exist or will be imported via zipimport
        # pex.pex 2.0.2
        #
        wheel_dir_hash = CacheHelper.dir_hash(self.install_chroot)
        runtime_key_dir = os.path.join(self.installation_root, wheel_dir_hash)
        with atomic_directory(runtime_key_dir, exclusive=False) as work_dir:
            if work_dir:
                # Note: Create a relative path symlink between the two directories so that the PEX_ROOT
                # can be used within a chroot environment where the prefix of the path may change
                # between programs running inside and outside of the chroot.
                source_path = os.path.join(work_dir, self.request.wheel_file)
                start_dir = os.path.dirname(source_path)
                relative_target_path = os.path.relpath(self.install_chroot, start_dir)
                os.symlink(relative_target_path, source_path)

        return self._iter_requirements_requests(install_requests)
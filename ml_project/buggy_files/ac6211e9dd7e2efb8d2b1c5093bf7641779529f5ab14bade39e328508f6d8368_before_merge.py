    def _build_one_legacy(self, req, tempd, python_tag=None):
        """Build one InstallRequirement using the "legacy" build process.

        Returns path to wheel if successfully built. Otherwise, returns None.
        """
        base_args = self._base_setup_args(req)

        spin_message = 'Building wheel for %s (setup.py)' % (req.name,)
        with open_spinner(spin_message) as spinner:
            logger.debug('Destination directory: %s', tempd)
            wheel_args = base_args + ['bdist_wheel', '-d', tempd] \
                + self.build_options

            if python_tag is not None:
                wheel_args += ["--python-tag", python_tag]

            try:
                call_subprocess(wheel_args, cwd=req.setup_py_dir,
                                show_stdout=False, spinner=spinner)
            except Exception:
                spinner.finish("error")
                logger.error('Failed building wheel for %s', req.name)
                return None
            # listdir's return value is sorted to be deterministic
            return os.path.join(tempd, sorted(os.listdir(tempd))[0])
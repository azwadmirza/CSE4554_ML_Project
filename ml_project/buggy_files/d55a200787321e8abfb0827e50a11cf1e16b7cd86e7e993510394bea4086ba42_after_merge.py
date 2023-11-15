    def _generate_new_files(self):
        new_files = set()
        installer = self._dist_info / "INSTALLER"
        installer.write_text("pip\n")
        new_files.add(installer)
        # inject a no-op root element, as workaround for bug added
        # by https://github.com/pypa/pip/commit/c7ae06c79#r35523722
        marker = self._image_dir / "{}.virtualenv".format(self._dist_info.name)
        marker.write_text("")
        new_files.add(marker)
        folder = mkdtemp()
        try:
            to_folder = Path(folder)
            rel = os.path.relpath(
                six.ensure_text(str(self._creator.script_dir)), six.ensure_text(str(self._creator.purelib))
            )
            for name, module in self._console_scripts.items():
                new_files.update(
                    Path(os.path.normpath(six.ensure_text(str(self._image_dir / rel / i.name))))
                    for i in self._create_console_entry_point(name, module, to_folder)
                )
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        return new_files
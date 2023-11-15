    def install(self):
        self._extracted = True
        # sync image
        site_package = self._creator.site_packages[0]
        for filename in self._image_dir.iterdir():
            into = site_package / filename.name
            logging.debug("%s %s from %s", self.__class__.__name__, into, filename)
            if into.exists():
                if into.is_dir() and not into.is_symlink():
                    shutil.rmtree(str(into))
                else:
                    into.unlink()
            self._sync(filename, into)
        # generate console executables
        consoles = set()
        bin_dir = self._creator.bin_dir
        for name, module in self._console_scripts.items():
            consoles.update(self._create_console_entry_point(name, module, bin_dir))
        logging.debug("generated console scripts %s", " ".join(i.name for i in consoles))
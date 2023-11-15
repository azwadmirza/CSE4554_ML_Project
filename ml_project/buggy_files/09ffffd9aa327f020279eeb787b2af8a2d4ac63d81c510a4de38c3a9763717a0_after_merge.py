    def install(self):
        self._extracted = True
        # sync image
        for filename in self._image_dir.iterdir():
            into = self._creator.purelib / filename.name
            logging.debug("%s %s from %s", self.__class__.__name__, into, filename)
            if into.exists():
                if into.is_dir() and not into.is_symlink():
                    shutil.rmtree(str(into))
                else:
                    into.unlink()
            self._sync(filename, into)
        # generate console executables
        consoles = set()
        script_dir = self._creator.script_dir
        for name, module in self._console_scripts.items():
            consoles.update(self._create_console_entry_point(name, module, script_dir))
        logging.debug("generated console scripts %s", " ".join(i.name for i in consoles))
    def cb_shred_quit(self, action, param):
        """Shred settings (for privacy reasons) and quit"""
        # build a list of paths to delete
        paths = []
        if 'nt' == os.name and portable_mode:
            # in portable mode on Windows, the options directory includes
            # executables
            paths.append(bleachbit.options_file)
        else:
            paths.append(bleachbit.options_dir)

        # prompt the user to confirm
        if not self.shred_paths(paths):
            logger.debug('user aborted shred')
            # aborted
            return

        # in portable mode, rebuild a minimal bleachbit.ini
        if 'nt' == os.name and portable_mode:
            with open(bleachbit.options_file, 'w') as f:
                f.write('[Portable]\n')

        # Quit the application through the idle loop to allow the worker
        # to delete the files.  Use the lowest priority because the worker
        # uses the standard priority.  Otherwise, this will quit before
        # the files are deleted.
        GLib.idle_add(
            lambda: Gtk.main_quit(), priority=GObject.PRIORITY_LOW)
    def save(self, title=None, temporary=False):
        """Saves all changes to the configuration files.

        This function first checks for save errors, if none are found,
        all configuration changes made will be saved. According to the
        function parameters. If an exception is raised, a new checkpoint
        was not created.

        :param str title: The title of the save. If a title is given, the
            configuration will be saved as a new checkpoint and put in a
            timestamped directory.

        :param bool temporary: Indicates whether the changes made will
            be quickly reversed in the future (ie. challenges)

        """
        save_files = self.unsaved_files()
        if save_files:
            self.add_to_checkpoint(save_files,
                                   self.save_notes, temporary=temporary)

        self.save_notes = ""
        self.aug.save()

        # Force reload if files were modified
        # This is needed to recalculate augeas directive span
        if save_files:
            for sf in save_files:
                self.aug.remove("/files/"+sf)
            self.aug.load()
        if title and not temporary:
            self.finalize_checkpoint(title)
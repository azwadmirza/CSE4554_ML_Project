    def remove(self, auto_confirm=False, verbose=False):
        """Remove paths in ``self.paths`` with confirmation (unless
        ``auto_confirm`` is True)."""

        if not self.paths:
            logger.info(
                "Can't uninstall '%s'. No files were found to uninstall.",
                self.dist.project_name,
            )
            return

        dist_name_version = (
            self.dist.project_name + "-" + self.dist.version
        )
        logger.info('Uninstalling %s:', dist_name_version)

        with indent_log():
            if auto_confirm or self._allowed_to_proceed(verbose):
                self.save_dir.create()

                for path in sorted(compact(self.paths)):
                    new_path = self._stash(path)
                    logger.debug('Removing file or directory %s', path)
                    self._moved_paths.append(path)
                    renames(path, new_path)
                for pth in self.pth.values():
                    pth.remove()

                logger.info('Successfully uninstalled %s', dist_name_version)
    def rollback(self):
        """Rollback the changes previously made by remove()."""
        if not self._save_dirs:
            logger.error(
                "Can't roll back %s; was not uninstalled",
                self.dist.project_name,
            )
            return False
        logger.info('Rolling back uninstall of %s', self.dist.project_name)
        for path, tmp_path in self._moved_paths:
            logger.debug('Replacing %s', path)
            renames(tmp_path, path)
        for pth in self.pth.values():
            pth.rollback()
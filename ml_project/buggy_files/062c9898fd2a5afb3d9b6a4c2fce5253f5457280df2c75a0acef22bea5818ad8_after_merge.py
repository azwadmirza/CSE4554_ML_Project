    def delete(self, target):
        if self.is_running:
            logger.warning("Last sync client cmd still in progress, skipping.")
            return False
        final_cmd = self.delete_template.format(target=quote(target))
        logger.debug("Running delete: {}".format(final_cmd))
        self.cmd_process = subprocess.Popen(
            final_cmd,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=self._get_logfile())
        return True
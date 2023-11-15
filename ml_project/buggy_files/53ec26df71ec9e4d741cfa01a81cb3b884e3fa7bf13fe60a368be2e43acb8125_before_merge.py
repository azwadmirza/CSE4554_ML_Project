    def on_save_resume_data_alert(self, alert):
        """
        alert to handle save_resume_data_alert
        it will assign stored resume data in an attribute,
            and write it to a file
        """
        resume_data = alert.resume_data

        if not self.pstate_for_restart:
            self.pstate_for_restart = self.network_get_persistent_state()

        self.pstate_for_restart.set('state', 'engineresumedata', resume_data)
        self._logger.debug("%s get resume data %s", hexlify(resume_data['info-hash']), resume_data)

        # save it to file
        basename = hexlify(resume_data['info-hash']) + '.state'
        filename = os.path.join(self.session.get_downloads_pstate_dir(), basename)

        self._logger.debug("tlm: network checkpointing: to file %s", filename)

        self.pstate_for_restart.write_file(filename)

        # fire callback for all deferreds_resume
        for deferred_r in self.deferreds_resume:
            deferred_r.callback(resume_data)

        # empties the deferred list
        self.deferreds_resume = []
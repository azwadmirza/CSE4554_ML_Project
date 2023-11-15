    def on_save_resume_data_alert(self, alert):
        """
        Callback for the alert that contains the resume data of a specific download.
        This resume data will be written to a file on disk.
        """
        if self._checkpoint_disabled:
            return

        resume_data = alert.resume_data

        self.pstate_for_restart = self.get_persistent_download_config()

        # Make save_path relative if the torrent is saved in the Tribler state directory
        if self.state_dir and 'save_path' in resume_data and os.path.abspath(resume_data['save_path']):
            if self.state_dir == os.path.commonprefix([cast_to_unicode_utf8(resume_data['save_path']), self.state_dir]):
                resume_data['save_path'] = six.text_type(
                    os.path.relpath(cast_to_unicode_utf8(resume_data['save_path']), self.state_dir))

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
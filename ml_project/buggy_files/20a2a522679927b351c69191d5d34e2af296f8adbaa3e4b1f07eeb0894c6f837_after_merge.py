    def run(self):
        """Load skills and update periodically from disk and internet."""
        self._remove_git_locks()
        self._connected_event.wait()
        if (not self.skill_updater.defaults_installed() and
                self.skills_config["auto_update"]):
            LOG.info('Not all default skills are installed, '
                     'performing skill update...')
            self.skill_updater.update_skills()
        self._load_on_startup()

        # Sync backend and skills.
        if is_paired() and not self.upload_queue.started:
            self._start_settings_update()

        # Scan the file folder that contains Skills.  If a Skill is updated,
        # unload the existing version from memory and reload from the disk.
        while not self._stop_event.is_set():
            try:
                self._unload_removed_skills()
                self._reload_modified_skills()
                self._load_new_skills()
                self._update_skills()
                if (is_paired() and self.upload_queue.started and
                        len(self.upload_queue) > 0):
                    self.msm.clear_cache()
                    self.skill_updater.post_manifest()
                    self.upload_queue.send()

                self._watchdog()
                sleep(2)  # Pause briefly before beginning next scan
            except Exception:
                LOG.exception('Something really unexpected has occured '
                              'and the skill manager loop safety harness was '
                              'hit.')
                sleep(30)
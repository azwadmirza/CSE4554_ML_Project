    def persist(self):
        '''
        Persist the modified schedule into <<configdir>>/<<default_include>>/_schedule.conf
        '''
        config_dir = self.opts.get('conf_dir', None)
        if config_dir is None and 'conf_file' in self.opts:
            config_dir = os.path.dirname(self.opts['conf_file'])
        if config_dir is None:
            config_dir = salt.syspaths.CONFIG_DIR

        minion_d_dir = os.path.join(
            config_dir,
            os.path.dirname(self.opts.get('default_include',
                                          salt.config.DEFAULT_MINION_OPTS['default_include'])))

        if not os.path.isdir(minion_d_dir):
            os.makedirs(minion_d_dir)

        schedule_conf = os.path.join(minion_d_dir, '_schedule.conf')
        log.debug('Persisting schedule')
        schedule_data = self._get_schedule(include_pillar=False)
        try:
            with salt.utils.files.fopen(schedule_conf, 'wb+') as fp_:
                fp_.write(
                    salt.utils.stringutils.to_bytes(
                        salt.utils.yaml.safe_dump(
                            {'schedule': schedule_data}
                        )
                    )
                )
        except (IOError, OSError):
            log.error('Failed to persist the updated schedule',
                      exc_info_on_loglevel=logging.DEBUG)
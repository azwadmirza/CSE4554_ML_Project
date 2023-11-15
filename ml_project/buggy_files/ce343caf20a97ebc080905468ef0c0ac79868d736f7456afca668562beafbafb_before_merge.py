        def action():
            with debug.log_time(log.init, 'Import old history file to sqlite'):
                try:
                    self._read(path)
                except ValueError as ex:
                    message.error('Failed to import history: {}'.format(ex))
                else:
                    bakpath = path + '.bak'
                    message.info('History import complete. Moving {} to {}'
                                 .format(path, bakpath))
                    os.rename(path, bakpath)
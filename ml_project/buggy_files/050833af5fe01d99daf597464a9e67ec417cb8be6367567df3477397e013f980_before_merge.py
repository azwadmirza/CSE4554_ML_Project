    def import_txt(self):
        """Import a history text file into sqlite if it exists.

        In older versions of qutebrowser, history was stored in a text format.
        This converts that file into the new sqlite format and moves it to a
        backup location.
        """
        path = os.path.join(standarddir.data(), 'history')
        if not os.path.isfile(path):
            return

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

        # delay to give message time to appear before locking down for import
        message.info('Converting {} to sqlite...'.format(path))
        QTimer.singleShot(100, action)
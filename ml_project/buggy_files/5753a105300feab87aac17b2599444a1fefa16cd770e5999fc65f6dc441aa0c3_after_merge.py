    def Install(self):
        try:
            for update in self.search_results.Updates:
                if update.IsDownloaded:
                    self.install_collection.Add(update)
            log.debug('Updates prepared. beginning installation')
        except Exception as exc:
            log.info('Preparing install list failed: {0}'.format(exc))
            return exc

        # accept eula if not accepted
        try:
            for update in self.search_results.Updates:
                if not update.EulaAccepted:
                    log.debug(u'Accepting EULA: {0}'.format(update.Title))
                    update.AcceptEula()
        except Exception as exc:
            log.info('Accepting Eula failed: {0}'.format(exc))
            return exc

        if self.install_collection.Count != 0:
            log.debug('Install list created, about to install')
            updates = []
            try:
                self.install_results = self.win_installer.Install()
                log.info('Installation of updates complete')
                return True
            except Exception as exc:
                log.info('Installation failed: {0}'.format(exc))
                return exc
        else:
            log.info('no new updates.')
            return True
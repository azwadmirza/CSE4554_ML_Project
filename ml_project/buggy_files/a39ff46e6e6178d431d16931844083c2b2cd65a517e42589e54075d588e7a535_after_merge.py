    def Search(self, searchString):
        try:
            log.debug('beginning search of the passed string: {0}'.format(searchString))
            self.search_results = self.win_searcher.Search(searchString)
            log.debug('search completed successfully.')
        except Exception as exc:
            log.info('search for updates failed. {0}'.format(exc))
            return exc

        log.debug('parsing results. {0} updates were found.'.format(
            self.search_results.Updates.Count))
        try:
            for update in self.search_results.Updates:
                if update.InstallationBehavior.CanRequestUserInput:
                    log.debug(u'Skipped update {0}'.format(update.title))
                    continue
                for category in update.Categories:
                    if self.skipDownloaded and update.IsDownloaded:
                        continue
                    if self.categories is None or category.Name in self.categories:
                        self.download_collection.Add(update)
                        log.debug(u'added update {0}'.format(update.title))
            self.foundCategories = _gather_update_categories(self.download_collection)
            return True
        except Exception as exc:
            log.info('parsing updates failed. {0}'.format(exc))
            return exc
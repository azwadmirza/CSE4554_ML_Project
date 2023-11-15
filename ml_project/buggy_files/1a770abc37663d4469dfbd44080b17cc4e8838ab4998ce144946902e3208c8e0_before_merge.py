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
            # step through the list of the updates to ensure that the updates match the
            # features desired.
            for update in self.search_results.Updates:
                # this skipps an update if UI updates are not desired.
                if update.InstallationBehavior.CanRequestUserInput:
                    log.debug('Skipped update {0} - requests user input'.format(str(update)))
                    continue

                # if this update is already downloaded, it doesn't need to be in
                # the download_collection. so skipping it unless the user mandates re-download.
                if self.skipDownloaded and update.IsDownloaded:
                    log.debug('Skipped update {0} - already downloaded'.format(str(update)))
                    continue

                # check this update's categories against the ones desired.
                for category in update.Categories:
                    # this is a zero guard. these tests have to be in this order
                    # or it will error out when the user tries to search for
                    # updates with out specifying categories.
                    if self.categories is None or category.Name in self.categories:
                        # adds it to the list to be downloaded.
                        self.download_collection.Add(update)
                        log.debug('added update {0}'.format(str(update)))
                        # ever update has 2 categories. this prevents the
                        # from being added twice.
                        break
            log.debug('download_collection made. gathering found categories.')

            # gets the categories of the updates available in this collection of updates
            self.foundCategories = _gather_update_categories(self.download_collection)
            log.debug('found categories: {0}'.format(str(self.foundCategories)))
            return True
        except Exception as exc:
            log.info('parsing updates failed. {0}'.format(exc))
            return exc
    def GetSearchResultsVerbose(self):
        updates = []
        log.debug('parsing results. {0} updates were found.'.format(
            self.download_collection.count))

        for update in self.download_collection:
            if update.InstallationBehavior.CanRequestUserInput:
                log.debug(u'Skipped update {0}'.format(update.title))
                continue
            # More fields can be added from https://msdn.microsoft.com/en-us/library/windows/desktop/aa386099(v=vs.85).aspx
            update_com_fields = ['Categories', 'Deadline', 'Description',
                                 'Identity', 'IsMandatory',
                                 'KBArticleIDs', 'MaxDownloadSize', 'MinDownloadSize',
                                 'MoreInfoUrls', 'MsrcSeverity', 'ReleaseNotes',
                                 'SecurityBulletinIDs', 'SupportUrl', 'Title']
            simple_enums = ['KBArticleIDs', 'MoreInfoUrls', 'SecurityBulletinIDs']
            # update_dict = {k: getattr(update, k) for k in update_com_fields}
            update_dict = {}
            for f in update_com_fields:
                v = getattr(update, f)
                if not any([isinstance(v, bool), isinstance(v, str)]):
                    # Fields that require special evaluation.
                    if f in simple_enums:
                        v = [x for x in v]
                    elif f == 'Categories':
                        v = [{'Name': cat.Name, 'Description': cat.Description} for cat in v]
                    elif f == 'Deadline':
                        # Deadline will be useful and should be added.
                        # However, until it can be tested with a date object
                        # as returned by the COM, it is unclear how to
                        # handle this field.
                        continue
                    elif f == 'Identity':
                        v = {'RevisionNumber': v.RevisionNumber,
                             'UpdateID': v.UpdateID}
                update_dict[f] = v
            updates.append(update_dict)
            log.debug(u'added update {0}'.format(update.title))
        return updates
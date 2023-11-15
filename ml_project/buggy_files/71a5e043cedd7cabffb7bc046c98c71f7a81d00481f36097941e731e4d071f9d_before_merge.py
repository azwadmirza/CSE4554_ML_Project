    def upload(self, request, project, language, fileobj, method):
        '''
        Handles dictionary upload.
        '''
        from weblate.trans.models.changes import Change
        store = AutoFormat.parse(fileobj)

        ret = 0

        # process all units
        for dummy, unit in store.iterate_merge(False):
            source = unit.get_source()
            target = unit.get_target()

            # Ignore too long words
            if len(source) > 200 or len(target) > 200:
                continue

            # Get object
            word, created = self.get_or_create(
                project=project,
                language=language,
                source=source,
                defaults={
                    'target': target,
                },
            )

            # Already existing entry found
            if not created:
                # Same as current -> ignore
                if target == word.target:
                    continue
                if method == 'add':
                    # Add word
                    word = self.create(
                        request,
                        action=Change.ACTION_DICTIONARY_UPLOAD,
                        project=project,
                        language=language,
                        source=source,
                        target=target
                    )
                elif method == 'overwrite':
                    # Update word
                    word.target = target
                    word.save()

            ret += 1

        return ret
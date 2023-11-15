    def evaluate_tags(self, only_tags, skip_tags, all_vars):
        ''' this checks if the current item should be executed depending on tag options '''

        should_run = True

        if self.tags:
            templar = Templar(loader=self._loader, variables=all_vars)
            tags = templar.template(self.tags)

            if not isinstance(tags, list):
                if tags.find(',') != -1:
                    tags = set(tags.split(','))
                else:
                    tags = set([tags])
            else:
                tags = set([i for i,_ in itertools.groupby(tags)])
        else:
            # this makes intersection work for untagged
            tags = self.__class__.untagged

        if only_tags:

            should_run = False

            if 'always' in tags or 'all' in only_tags:
                 should_run = True
            elif tags.intersection(only_tags):
                should_run = True
            elif 'tagged' in only_tags and tags != self.__class__.untagged:
                should_run = True

        if should_run and skip_tags:

            # Check for tags that we need to skip
            if 'all' in skip_tags:
                if 'always' not in tags or 'always' in skip_tags:
                    should_run = False
            elif tags.intersection(skip_tags):
                should_run = False
            elif 'tagged' in skip_tags and tags != self.__class__.untagged:
                should_run = False

        return should_run
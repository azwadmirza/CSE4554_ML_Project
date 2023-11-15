    def when(self, matches, context):
        """Evaluate the rule.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context: dict
        :return:
        """
        # In case of duplicated titles, keep only the first one
        titles = matches.named('title')

        if (titles and len(titles) > 1 and matches.tagged('anime') and
                'equivalent' not in titles[-1].tags and 'expected' not in titles[-1].tags):
            wrong_title = matches.named('title', predicate=lambda m: m.value != titles[0].value, index=-1)
            if wrong_title:
                release_group = copy.copy(wrong_title)
                release_group.name = 'release_group'
                release_group.tags = []

                to_remove = matches.named('release_group', predicate=lambda match: match.span != release_group.span)
                return to_remove, release_group
    def when(self, matches, context):
        """Evaluate the rule.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context: dict
        :return:
        """
        fileparts = matches.markers.named('path')
        parts_len = len(fileparts)
        if parts_len < 2:
            return

        episode_title = matches.named('episode_title')
        if episode_title:
            second_part = fileparts[parts_len - 2].value
            if self.ends_with_digit.search(second_part):
                title = matches.named('title')
                if not title:
                    episode_title[0].name = 'title'
                    to_append = episode_title
                    to_remove = None
                    return to_remove, to_append

                if second_part.startswith(title[0].value):
                    season = matches.named('season')
                    if season and not second_part.endswith(season[-1].initiator.value):
                        episode_title[0].name = 'title'
                        to_append = episode_title
                        to_remove = title
                        return to_remove, to_append
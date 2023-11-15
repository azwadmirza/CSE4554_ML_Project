    def when(self, matches, context):
        """Evaluate the rule.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context: dict
        :return:
        """
        fileparts = matches.markers.named('path')
        for filepart in marker_sorted(fileparts, matches):
            formats = matches.range(filepart.start, filepart.end, predicate=lambda match: match.name == 'format')
            if len(formats) < 2:
                continue

            last_format = formats[-1]
            previous = matches.previous(last_format, predicate=lambda match: match.name == 'screen_size')
            next_range = matches.range(last_format.end, filepart.end,
                                       lambda match: match.name in ('audio_codec', 'video_codec', 'release_group'))
            # If we have at least 3 matches near by, then discard the other formats
            if len(previous) + len(next_range) > 2:
                invalid_formats = {f.value for f in formats[0:-1]}
                to_remove = matches.named('format', predicate=lambda m: m.value in invalid_formats)
                return to_remove
    def to_guessit_format(quality):
        """Return a guessit format from a Quality

        :param quality: the quality
        :type quality: int
        :return: guessit format
        :rtype: str
        """
        for q in Quality.to_guessit_format_list:
            if quality & q:
                return Quality.combinedQualityStrings.get(q)
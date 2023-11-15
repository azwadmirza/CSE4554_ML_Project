    def to_guessit_format(quality):
        """Return a guessit format from a Quality

        :param quality: the quality
        :type quality: int
        :return: guessit format
        :rtype: str
        """
        for q in Quality.to_guessit_format_list:
            if quality & q:
                key = q & (512 - 1)  # 4k formats are bigger than 384 and are not part of ANY* bit set
                return Quality.combinedQualityStrings.get(key)
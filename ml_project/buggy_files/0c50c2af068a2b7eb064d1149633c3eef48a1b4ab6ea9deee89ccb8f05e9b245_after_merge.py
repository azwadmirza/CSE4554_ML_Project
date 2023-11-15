    def to_guessit(status):
        """Return a guessit dict containing 'screen_size and format' from a Quality (composite status)

        :param status: a quality composite status
        :type status: int
        :return: dict {'screen_size': <screen_size>, 'format': <format>}
        :rtype: dict (str, str)
        """
        _, quality = Quality.splitCompositeStatus(status)
        screen_size = Quality.to_guessit_screen_size(quality)
        fmt = Quality.to_guessit_format(quality)
        result = dict()
        if screen_size:
            result['screen_size'] = screen_size
        if fmt:
            result['format'] = fmt

        return result
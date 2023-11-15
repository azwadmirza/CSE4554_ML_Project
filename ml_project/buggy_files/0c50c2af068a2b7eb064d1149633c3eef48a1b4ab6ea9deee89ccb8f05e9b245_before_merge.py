    def to_guessit(status):
        """Return a guessit dict containing 'screen_size and format' from a Quality (composite status)

        :param status: a quality composite status
        :type status: int
        :return: dict {'screen_size': <screen_size>, 'format': <format>}
        :rtype: dict (str, str)
        """
        _, quality = Quality.splitCompositeStatus(status)
        result = {
            'screen_size': Quality.to_guessit_screen_size(quality),
            'format': Quality.to_guessit_format(quality)
        }
        return result
    def from_guessit(guess):
        """

        :param guess: guessit dict
        :type guess: dict
        :return: quality
        :rtype: int
        """
        screen_size = guess.get('screen_size')
        fmt = guess.get('format')

        if not screen_size:
            return Quality.UNKNOWN

        format_map = Quality.guessit_map.get(screen_size)
        if not format_map:
            return Quality.UNKNOWN

        if isinstance(format_map, int):
            return format_map

        if not fmt:
            return Quality.UNKNOWN

        quality = format_map.get(fmt)
        return quality if quality is not None else Quality.UNKNOWN
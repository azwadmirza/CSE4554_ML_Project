    def escape_format_string(cls, string):
        """
        Escapes curly braces from a PEP-3101's format string when there's a sequence of odd length
        """

        def escape_group_of_curly_braces(match):
            curlies = match.group()
            if len(curlies) % 2 == 1:
                curlies += curlies
            return curlies

        escaped_string = cls.CURLY_BRACES_REGEX.sub(escape_group_of_curly_braces, string)
        return escaped_string
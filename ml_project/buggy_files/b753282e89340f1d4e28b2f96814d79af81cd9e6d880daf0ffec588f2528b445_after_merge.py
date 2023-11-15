    def escape_format_string(cls, string):
        """
        Escapes all curly braces from a PEP-3101's format string.
        """
        escaped_string = string.replace("{", "{{").replace("}", "}}")
        return escaped_string
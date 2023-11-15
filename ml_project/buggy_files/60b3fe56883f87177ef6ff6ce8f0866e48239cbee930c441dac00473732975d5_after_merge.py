    def parse(cls, source):
        """GreasemonkeyScript factory.

        Takes a userscript source and returns a GreasemonkeyScript.
        Parses the Greasemonkey metadata block, if present, to fill out
        attributes.
        """
        matches = re.split(cls.HEADER_REGEX, source, maxsplit=2)
        try:
            _head, props, _code = matches
        except ValueError:
            props = ""
        script = cls(re.findall(cls.PROPS_REGEX, props), source)
        script.script_meta = props
        if not script.includes:
            script.includes = ['*']
        return script
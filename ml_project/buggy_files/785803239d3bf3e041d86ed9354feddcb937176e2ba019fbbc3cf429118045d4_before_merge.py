    def loads(text):
        """ parses a multiline text in the form
        Package:option=value
        other_option=3
        OtherPack:opt3=12.1
        """
        result = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            name, value = line.split("=")
            result.append((name.strip(), value.strip()))
        return OptionsValues(result)
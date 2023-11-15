    def fromstring(cls, s):
        """Creates a new instance of the LsColors class from a colon-separated
        string of dircolor-valid keys to ANSI color escape sequences.
        """
        obj = cls()
        # string inputs always use default codes, so translating into
        # xonsh names should be done from defaults
        reversed_default = ansi_reverse_style(style="default")
        data = {}
        for item in s.split(":"):
            key, eq, esc = item.partition("=")
            if not eq:
                # not a valid item
                pass
            elif esc == "target":
                data[key] = ("TARGET",)
            else:
                try:
                    data[key] = ansi_color_escape_code_to_name(
                        esc, "default", reversed_style=reversed_default
                    )
                except Exception as e:
                    print("xonsh:warning:" + str(e), file=sys.stderr)
                    data[key] = ("NO_COLOR",)
        obj._d = data
        return obj
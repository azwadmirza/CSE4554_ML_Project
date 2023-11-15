    def __init__(self):
        self.indent_level = 0

        self._verbosity = 0
        self._verbosity_overriden = False
        self._color_mode = "auto"
        self._log_style = "record"
        self.pretty = False
        self.interactive = False

        # store whatever colorful has detected for future use if
        # the color ouput is toggled (colorful detects # of supported colors,
        # so it has some non-trivial logic to determine this)
        self._autodetected_cf_colormode = cf.colorful.colormode
        self.set_format()
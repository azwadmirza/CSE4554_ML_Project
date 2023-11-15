    def __call__(self, data, **metadata):
        cssutils.log.setLevel(logging.CRITICAL)
        cssutils.ser.prefs.keepComments = True
        cssutils.ser.prefs.omitLastSemicolon = False
        cssutils.ser.prefs.indentClosingBrace = False
        cssutils.ser.prefs.validOnly = False

        sheet = cssutils.parseString(data)
        beautified = sheet.cssText

        return "CSS", format_text(beautified)
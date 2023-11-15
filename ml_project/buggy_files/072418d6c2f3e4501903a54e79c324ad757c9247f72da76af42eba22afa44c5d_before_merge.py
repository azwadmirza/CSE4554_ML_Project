    def __call__(self, data, **metadata):
        if cssutils:
            sheet = cssutils.parseString(data)
            beautified = sheet.cssText
        else:
            beautified = data

        return "CSS", format_text(beautified)
    def __init__(self, descriptor, widths, default_width=None):
        self.descriptor = descriptor
        self.widths = resolve_all(widths)
        self.fontname = resolve1(descriptor.get('FontName', 'unknown'))
        if isinstance(self.fontname, PSLiteral):
            self.fontname = literal_name(self.fontname)
        self.flags = int_value(descriptor.get('Flags', 0))
        self.ascent = num_value(descriptor.get('Ascent', 0))
        self.descent = num_value(descriptor.get('Descent', 0))
        self.italic_angle = num_value(descriptor.get('ItalicAngle', 0))
        self.default_width = default_width or num_value(descriptor.get('MissingWidth', 0))
        self.leading = num_value(descriptor.get('Leading', 0))
        self.bbox = list_value(resolve_all(descriptor.get('FontBBox', (0, 0, 0, 0))))
        self.hscale = self.vscale = .001
        return
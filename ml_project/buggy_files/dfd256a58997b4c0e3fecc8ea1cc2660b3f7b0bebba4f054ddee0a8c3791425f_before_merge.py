def pattern(pat, cap=True, esc=False):
    """Return a 'natural' version of the pattern string for human-readable
    bits. Assumes all tags in the pattern are present."""
    from quodlibet.pattern import Pattern, XMLFromPattern

    class Fakesong(dict):
        cap = False

        def comma(self, key):
            return " - ".join(self.list(key))

        def list(self, key):
            return [tag(k, self.cap) for k in tagsplit(key)]
        list_seperate = list
        __call__ = comma

    fakesong = Fakesong({'filename': tag('filename', cap)})
    fakesong.cap = cap
    try:
        p = (esc and XMLFromPattern(pat)) or Pattern(pat)
    except ValueError:
        return _("Invalid pattern")

    return p.format(fakesong)
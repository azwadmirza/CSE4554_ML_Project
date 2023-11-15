    def unescape(self, text):
        """ Return unescaped text given text with an inline placeholder. """
        try:
            stash = self.markdown.treeprocessors['inline'].stashed_nodes
        except KeyError:
            return text
        def itertext(el):
            ' Reimplement Element.itertext for older python versions '
            tag = el.tag
            if not isinstance(tag, basestring) and tag is not None:
                return
            if el.text:
                yield el.text
            for e in el:
                for s in itertext(e):
                    yield s
                if e.tail:
                    yield e.tail
        def get_stash(m):
            id = m.group(1)
            if id in stash:
                value = stash.get(id)
                if isinstance(value, basestring):
                    return value
                else:
                    # An etree Element - return text content only
                    return ''.join(itertext(value)) 
        return util.INLINE_PLACEHOLDER_RE.sub(get_stash, text)
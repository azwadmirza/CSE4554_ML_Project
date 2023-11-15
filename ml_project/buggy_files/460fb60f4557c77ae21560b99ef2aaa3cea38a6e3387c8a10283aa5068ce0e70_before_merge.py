    def unescape(self, text):
        """ Return unescaped text given text with an inline placeholder. """
        try:
            stash = self.markdown.treeprocessors['inline'].stashed_nodes
        except KeyError:
            return text
        def get_stash(m):
            id = m.group(1)
            if id in stash:
                return stash.get(id)
        return util.INLINE_PLACEHOLDER_RE.sub(get_stash, text)
        def get_stash(m):
            id = m.group(1)
            if id in stash:
                text = stash.get(id)
                if isinstance(text, basestring):
                    return text
                else:
                    return self.markdown.serializer(text)
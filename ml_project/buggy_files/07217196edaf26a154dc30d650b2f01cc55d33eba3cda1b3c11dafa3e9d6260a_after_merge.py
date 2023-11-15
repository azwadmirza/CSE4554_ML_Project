        def get_stash(m):
            id = m.group(1)
            if id in stash:
                value = stash.get(id)
                if isinstance(value, basestring):
                    return value
                else:
                    # An etree Element - return text content only
                    return ''.join(itertext(value)) 
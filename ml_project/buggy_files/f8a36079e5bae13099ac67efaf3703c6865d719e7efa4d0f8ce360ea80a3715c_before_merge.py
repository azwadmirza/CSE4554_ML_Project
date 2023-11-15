    def run(self, lines):
        '''
        Find and remove all Abbreviation references from the text.
        Each reference is set as a new AbbrPattern in the markdown instance.

        '''
        new_text = []
        for line in lines:
            m = ABBR_REF_RE.match(line)
            if m:
                abbr = m.group('abbr').strip()
                title = m.group('title').strip()
                self.md.inlinePatterns.register(
                    AbbrInlineProcessor(self._generate_pattern(abbr), title), 'abbr-%s' % abbr, 2
                )
                # Preserve the line to prevent raw HTML indexing issue.
                # https://github.com/Python-Markdown/markdown/issues/584
                new_text.append('')
            else:
                new_text.append(line)
        return new_text
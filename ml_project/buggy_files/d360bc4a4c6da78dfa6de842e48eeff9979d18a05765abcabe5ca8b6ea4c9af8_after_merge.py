    def run(self, lines):
        """
        Loop through lines and find, set, and remove footnote definitions.

        Keywords:

        * lines: A list of lines of text

        Return: A list of lines of text with footnote definitions removed.

        """
        newlines = []
        i = 0
        while True:
            m = DEF_RE.match(lines[i])
            if m:
                fn, _i = self.detectTabbed(lines[i+1:])
                fn.insert(0, m.group(2))
                i += _i-1  # skip past footnote
                footnote = "\n".join(fn)
                self.footnotes.setFootnote(m.group(1), footnote.rstrip())
                # Preserve a line for each block to prevent raw HTML indexing issue.
                # https://github.com/Python-Markdown/markdown/issues/584
                num_blocks = (len(footnote.split('\n\n')) * 2)
                newlines.extend([''] * (num_blocks))
            else:
                newlines.append(lines[i])
            if len(lines) > i+1:
                i += 1
            else:
                break
        return newlines
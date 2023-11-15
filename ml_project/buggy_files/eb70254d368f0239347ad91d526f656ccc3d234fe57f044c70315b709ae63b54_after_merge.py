    def run(self, lines):
        new_text = []
        while lines:
            line = lines.pop(0)
            m = self.RE.match(line)
            if m:
                id = m.group(1).strip().lower()
                link = m.group(2).lstrip('<').rstrip('>')
                t = m.group(5) or m.group(6) or m.group(7)
                if not t:
                    # Check next line for title
                    tm = self.TITLE_RE.match(lines[0])
                    if tm:
                        lines.pop(0)
                        t = tm.group(2) or tm.group(3) or tm.group(4)
                self.markdown.references[id] = (link, t)
                # Preserve the line to prevent raw HTML indexing issue.
                # https://github.com/Python-Markdown/markdown/issues/584
                new_text.append('')
            else:
                new_text.append(line)

        return new_text  # + "\n"
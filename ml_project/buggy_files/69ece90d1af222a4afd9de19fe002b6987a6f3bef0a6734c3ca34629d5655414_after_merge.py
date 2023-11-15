    def detectTabbed(self, lines):
        """ Find indented text and remove indent before further proccesing.

        Keyword arguments:

        * lines: an array of strings

        Returns: a list of post processed items and the index of last line.

        """
        items = []
        blank_line = False  # have we encountered a blank line yet?
        i = 0  # to keep track of where we are

        def detab(line):
            match = TABBED_RE.match(line)
            if match:
                return match.group(4)

        for line in lines:
            if line.strip():  # Non-blank line
                detabbed_line = detab(line)
                if detabbed_line:
                    items.append(detabbed_line)
                    i += 1
                    continue
                elif not blank_line and not DEF_RE.match(line):
                    # not tabbed but still part of first par.
                    items.append(line)
                    i += 1
                    continue
                else:
                    return items, i+1

            else:  # Blank line: _maybe_ we are done.
                blank_line = True
                i += 1  # advance

                # Find the next non-blank line
                for j in range(i, len(lines)):
                    if lines[j].strip():
                        next_line = lines[j]
                        break
                    else:
                        # Include extreaneous padding to prevent raw HTML
                        # parsing issue: https://github.com/Python-Markdown/markdown/issues/584
                        items.append("")
                        i += 1
                else:
                    break  # There is no more text; we are done.

                # Check if the next non-blank line is tabbed
                if detab(next_line):  # Yes, more work to do.
                    items.append("")
                    continue
                else:
                    break  # No, we are done.
        else:
            i += 1

        return items, i
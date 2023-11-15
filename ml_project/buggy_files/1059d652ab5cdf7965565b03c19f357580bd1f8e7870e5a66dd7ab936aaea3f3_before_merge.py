        def detab(line):
            match = TABBED_RE.match(line)
            if match:
                return match.group(4)
    def parse_line(self, line, exclude_unreachable_branches):
        # If this is a tag line, we stay on the same line number
        # and can return immediately after processing it.
        # A tag line cannot hold exclusion markers.
        if self.parse_tag_line(line, exclude_unreachable_branches):
            return

        # If this isn't a tag line, this is metadata or source code.
        # e.g.  "  -:  0:Data:foo.gcda" (metadata)
        # or    "  3:  7:  c += 1"      (source code)

        segments = line.split(":", 2)
        if len(segments) > 1:
            try:
                self.lineno = int(segments[1].strip())
            except ValueError:
                pass  # keep previous line number!

        if exclude_line_flag in line:
            excl_line = False
            for header, flag in exclude_line_pattern.findall(line):
                if self.parse_exclusion_marker(header, flag):
                    excl_line = True

            # We buffer the line exclusion so that it is always
            # the last thing added to the exclusion list (and so
            # only ONE is ever added to the list).  This guards
            # against cases where puts a _LINE and _START (or
            # _STOP) on the same line... it also guards against
            # duplicate _LINE flags.
            if excl_line:
                self.excluding.append(False)

        status = segments[0].strip()
        code = segments[2] if 2 < len(segments) else ""
        is_code_statement = self.parse_code_line(status, code)

        if not is_code_statement:
            self.unrecognized_lines.append(line)

        # save the code line to use it later with branches
        if is_code_statement:
            self.last_code_line = "".join(segments[2:])
            self.last_code_lineno = self.lineno
            self.last_code_line_excluded = bool(self.excluding)

        # clear the excluding flag for single-line excludes
        if self.excluding and not self.excluding[-1]:
            self.excluding.pop()
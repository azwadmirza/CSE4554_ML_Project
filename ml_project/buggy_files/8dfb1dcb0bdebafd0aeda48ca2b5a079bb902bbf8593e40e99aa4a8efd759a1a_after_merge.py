    def parse_tag_line(self, line, exclude_unreachable_branches):
        # Start or end a template/macro specialization section
        if line.startswith('-----'):
            self.last_was_specialization_section_marker = True
            return True

        last_was_marker = self.last_was_specialization_section_marker
        self.last_was_specialization_section_marker = False

        # A specialization section marker is either followed by a section or
        # ends it. If it starts a section, the next line contains a function
        # name, followed by a colon. A function name cannot be parsed reliably,
        # so we assume it is a function, and try to disprove this assumption by
        # comparing with other kinds of lines.
        if last_was_marker:
            # 1. a function must end with a colon
            is_function = line.endswith(':')

            # 2. a function cannot start with space
            if is_function:
                is_function = not line.startswith(' ')

            # 3. a function cannot start with a tag
            if is_function:
                tags = 'function call branch'.split()
                is_function = not any(
                    line.startswith(tag + ' ') for tag in tags)

            # If this line turned out to be a function, discard it.
            return True

        if line.startswith('function '):
            return True

        if line.startswith('call '):
            return True

        if line.startswith('branch '):
            exclude_branch = False
            if exclude_unreachable_branches and \
                    self.lineno == self.last_code_lineno:
                if self.last_code_line_excluded:
                    exclude_branch = True
                    exclude_reason = "marked with exclude pattern"
                else:
                    code = self.last_code_line
                    code = re.sub(cpp_style_comment_pattern, '', code)
                    code = re.sub(c_style_comment_pattern, '', code)
                    code = code.strip()
                    code_nospace = code.replace(' ', '')
                    exclude_branch = \
                        code in ['', '{', '}'] or code_nospace == '{}'
                    exclude_reason = "detected as compiler-generated code"

            if exclude_branch:
                self.logger.verbose_msg(
                    "Excluding unreachable branch on line {line} "
                    "in file {fname}: {reason}",
                    line=self.lineno, fname=self.fname,
                    reason=exclude_reason)
                return True

            fields = line.split()  # e.g. "branch  0 taken 0% (fallthrough)"
            branch_index = int(fields[1])
            try:
                count = int(fields[3])
            except (ValueError, IndexError):
                count = 0
            self.branches.setdefault(self.lineno, {})[branch_index] = count
            return True

        return False
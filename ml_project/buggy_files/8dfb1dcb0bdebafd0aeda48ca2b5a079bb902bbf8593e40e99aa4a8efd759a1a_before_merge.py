    def parse_tag_line(self, line, exclude_unreachable_branches):
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
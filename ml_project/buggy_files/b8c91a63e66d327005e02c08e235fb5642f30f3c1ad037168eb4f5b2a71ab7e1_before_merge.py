    def parse_code_line(self, status, code):
        firstchar = status[0]

        if firstchar == '-' or (self.excluding and firstchar in "#=0123456789"):
            # remember certain non-executed lines
            if self.excluding or is_non_code(code):
                self.noncode.add(self.lineno)
            return True

        if firstchar == '#':
            if is_non_code(code):
                self.noncode.add(self.lineno)
            else:
                self.uncovered.add(self.lineno)
            return True

        if firstchar == '=':
            self.uncovered_exceptional.add(self.lineno)
            return True

        if firstchar in "0123456789":
            self.covered[self.lineno] = int(status)
            return True

        return False
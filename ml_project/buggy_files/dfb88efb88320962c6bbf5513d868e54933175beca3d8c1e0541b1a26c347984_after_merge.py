    def visit_func_def(self, defn: FuncDef) -> None:
        start_line = defn.get_line() - 1
        start_indent = None
        # When a function is decorated, sometimes the start line will point to
        # whitespace or comments between the decorator and the function, so
        # we have to look for the start.
        while start_line < len(self.source):
            start_indent = self.indentation_level(start_line)
            if start_indent is not None:
                break
            start_line += 1
        # If we can't find the function give up and don't annotate anything.
        # Our line numbers are not reliable enough to be asserting on.
        if start_indent is None:
            return

        cur_line = start_line + 1
        end_line = cur_line
        # After this loop, function body will be lines [start_line, end_line)
        while cur_line < len(self.source):
            cur_indent = self.indentation_level(cur_line)
            if cur_indent is None:
                # Consume the line, but don't mark it as belonging to the function yet.
                cur_line += 1
            elif start_indent is not None and cur_indent > start_indent:
                # A non-blank line that belongs to the function.
                cur_line += 1
                end_line = cur_line
            else:
                # We reached a line outside the function definition.
                break

        is_typed = defn.type is not None
        for line in range(start_line, end_line):
            old_indent, _ = self.lines_covered[line]
            # If there was an old indent level for this line, and the new
            # level isn't increasing the indentation, ignore it.
            # This is to be defensive against funniness in our line numbers,
            # which are not always reliable.
            if old_indent <= start_indent:
                self.lines_covered[line] = (start_indent, is_typed)

        # Visit the body, in case there are nested functions
        super().visit_func_def(defn)
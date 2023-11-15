    def find_parent(self, level, h):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        trace = False and g.unitTesting
        trace_stack = False
        assert level >= 0
        if trace: g.trace('=====', level, len(self.stack), h)
        while level < len(self.stack):
            p = self.stack.pop()
            if trace:
                g.trace('POP', len(self.get_lines(p)), p.h)
                if trace and trace_stack:
                    self.print_list(self.get_lines(p))
        top = self.stack[-1]
        if trace: g.trace('TOP', top.h)
        child = self.create_child_node(
            parent = top,
            body = None,
            headline = h, # Leave the headline alone
        )
        self.stack.append(child)
        if trace and trace_stack: self.print_stack(self.stack)
        return self.stack[level]
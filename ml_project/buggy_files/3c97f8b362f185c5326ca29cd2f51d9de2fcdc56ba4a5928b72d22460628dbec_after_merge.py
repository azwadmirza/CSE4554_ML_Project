    def find_parent(self, level, h):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        trace = False and not g.unitTesting
        assert level >= 0
        if trace:
            print('')
            g.trace('===== level: %s, len(stack): %s h: %s' % (
                level, len(self.stack), h))
        while level < len(self.stack):
            p = self.stack.pop()
            if trace:
                g.trace('POP', len(self.get_lines(p)), p.h)
                # self.print_list(self.get_lines(p))
        top = self.stack[-1]
        if trace: g.trace('TOP', top.h)
        if 1: # Experimental fix for #877.
            if level > len(self.stack):
                print('')
                g.trace('Unexpected markdown level for: %s' % h)
                print('')
            while level > len(self.stack):
                child = self.create_child_node(
                    parent = top,
                    body = None,
                    headline = 'INSERTED NODE'
                )
                self.stack.append(child)
        assert level == len(self.stack), (level, len(self.stack))
        child = self.create_child_node(
            parent = top,
            body = None,
            headline = h, # Leave the headline alone
        )
        self.stack.append(child)
        if trace:
            g.trace('level', level)
            self.print_stack(self.stack)
        assert self.stack
        assert 0 <= level < len(self.stack), (level, len(self.stack))
        return self.stack[level]
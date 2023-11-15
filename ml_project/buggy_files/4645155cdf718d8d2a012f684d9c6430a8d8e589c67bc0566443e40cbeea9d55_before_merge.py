    def e1(self):
        left = self.e2()
        if self.accept('plusassign'):
            value = self.e1()
            if not isinstance(left, IdNode):
                raise ParseException('Plusassignment target must be an id.', self.getline(), left.lineno, left.colno)
            return PlusAssignmentNode(left.subdir, left.lineno, left.colno, left.value, value)
        elif self.accept('assign'):
            value = self.e1()
            if not isinstance(left, IdNode):
                raise ParseException('Assignment target must be an id.',
                                     self.getline(), left.lineno, left.colno)
            return AssignmentNode(left.subdir, left.lineno, left.colno, left.value, value)
        elif self.accept('questionmark'):
            if self.in_ternary:
                raise ParseException('Nested ternary operators are not allowed.',
                                     self.getline(), left.lineno, left.colno)
            self.in_ternary = True
            trueblock = self.e1()
            self.expect('colon')
            falseblock = self.e1()
            self.in_ternary = False
            return TernaryNode(left.lineno, left.colno, left, trueblock, falseblock)
        return left
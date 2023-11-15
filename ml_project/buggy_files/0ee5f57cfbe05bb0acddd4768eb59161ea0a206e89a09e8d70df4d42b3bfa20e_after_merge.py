    def accept(self, visitor: 'TypeVisitor[T]') -> T:
        return visitor.visit_forwardref_type(self)
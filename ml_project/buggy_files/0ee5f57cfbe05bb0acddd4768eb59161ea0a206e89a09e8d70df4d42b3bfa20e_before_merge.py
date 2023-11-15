    def accept(self, visitor: 'TypeVisitor[T]') -> T:
        return visitor.visit_type_type(self)
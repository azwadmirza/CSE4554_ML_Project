    def analyze_types(self, items: List[Expression]) -> List[Type]:
        result = []  # type: List[Type]
        for node in items:
            try:
                result.append(self.anal_type(expr_to_unanalyzed_type(node)))
            except TypeTranslationError:
                self.fail('Type expected', node)
                result.append(AnyType(TypeOfAny.from_error))
        return result
    def find_isinstance_check(self, n: Expression) -> Tuple[Optional[Dict[Expression, Type]],
                                                            Optional[Dict[Expression, Type]]]:
        return find_isinstance_check(n, self.type_map)
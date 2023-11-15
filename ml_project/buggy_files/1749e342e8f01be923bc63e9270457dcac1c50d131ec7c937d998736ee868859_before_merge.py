    def find_isinstance_check(self, n: Expression) -> 'Tuple[TypeMap, TypeMap]':
        return find_isinstance_check(n, self.type_map)
    def _check_valid_assign(self, sub):
        if isinstance(self.stmt.annotation, ast.Call):  # unit style: num(wei)
            if self.stmt.annotation.func.id != sub.typ.typ and not sub.typ.is_literal:
                raise TypeMismatchException('Invalid type, expected: %s' % self.stmt.annotation.func.id, self.stmt)
        elif isinstance(self.stmt.annotation, ast.Dict):
            if not isinstance(sub.typ, StructType):
                raise TypeMismatchException('Invalid type, expected a struct')
        elif isinstance(self.stmt.annotation, ast.Subscript):
            if not isinstance(sub.typ, (ListType, ByteArrayType)):  # check list assign.
                raise TypeMismatchException('Invalid type, expected: %s' % self.stmt.annotation.value.id, self.stmt)
        # Check that the integer literal, can be assigned to uint256 if necessary.
        elif (self.stmt.annotation.id, sub.typ.typ) == ('uint256', 'int128') and sub.typ.is_literal:
            if not SizeLimits.in_bounds('uint256', sub.value):
                raise InvalidLiteralException('Invalid uint256 assignment, value not in uint256 range.', self.stmt)
        elif self.stmt.annotation.id != sub.typ.typ and not sub.typ.unit:
            raise TypeMismatchException('Invalid type, expected: %s' % self.stmt.annotation.id, self.stmt)
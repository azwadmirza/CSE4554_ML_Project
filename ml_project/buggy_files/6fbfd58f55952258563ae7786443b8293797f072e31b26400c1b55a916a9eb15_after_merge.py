    def check_boolean_op(self, e: OpExpr, context: Context) -> Type:
        """Type check a boolean operation ('and' or 'or')."""

        # A boolean operation can evaluate to either of the operands.

        # We use the current type context to guide the type inference of of
        # the left operand. We also use the left operand type to guide the type
        # inference of the right operand so that expressions such as
        # '[1] or []' are inferred correctly.
        ctx = self.chk.type_context[-1]
        left_type = self.accept(e.left, ctx)

        assert e.op in ('and', 'or')  # Checked by visit_op_expr

        if e.op == 'and':
            right_map, left_map = self.chk.find_isinstance_check(e.left)
            restricted_left_type = false_only(left_type)
            result_is_left = not left_type.can_be_true
        elif e.op == 'or':
            left_map, right_map = self.chk.find_isinstance_check(e.left)
            restricted_left_type = true_only(left_type)
            result_is_left = not left_type.can_be_false

        right_type = self.analyze_cond_branch(right_map, e.right, left_type)

        self.check_usable_type(left_type, context)
        self.check_usable_type(right_type, context)

        if right_map is None:
            # The boolean expression is statically known to be the left value
            assert left_map is not None  # find_isinstance_check guarantees this
            return left_type
        if left_map is None:
            # The boolean expression is statically known to be the right value
            assert right_map is not None  # find_isinstance_check guarantees this
            return right_type

        if isinstance(restricted_left_type, UninhabitedType):
            # The left operand can never be the result
            return right_type
        elif result_is_left:
            # The left operand is always the result
            return left_type
        else:
            return UnionType.make_simplified_union([restricted_left_type, right_type])
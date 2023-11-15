    def find_isinstance_check(self, node: Expression
                              ) -> Tuple[TypeMap, TypeMap]:
        """Find any isinstance checks (within a chain of ands).  Includes
        implicit and explicit checks for None and calls to callable.

        Return value is a map of variables to their types if the condition
        is true and a map of variables to their types if the condition is false.

        If either of the values in the tuple is None, then that particular
        branch can never occur.

        Guaranteed to not return None, None. (But may return {}, {})
        """
        type_map = self.type_map
        if is_true_literal(node):
            return {}, None
        elif is_false_literal(node):
            return None, {}
        elif isinstance(node, CallExpr):
            if refers_to_fullname(node.callee, 'builtins.isinstance'):
                if len(node.args) != 2:  # the error will be reported later
                    return {}, {}
                expr = node.args[0]
                if literal(expr) == LITERAL_TYPE:
                    vartype = type_map[expr]
                    type = get_isinstance_type(node.args[1], type_map)
                    return conditional_type_map(expr, vartype, type)
            elif refers_to_fullname(node.callee, 'builtins.issubclass'):
                expr = node.args[0]
                if literal(expr) == LITERAL_TYPE:
                    vartype = type_map[expr]
                    type = get_isinstance_type(node.args[1], type_map)
                    if isinstance(vartype, UnionType):
                        union_list = []
                        for t in vartype.items:
                            if isinstance(t, TypeType):
                                union_list.append(t.item)
                            else:
                                #  this is an error that should be reported earlier
                                #  if we reach here, we refuse to do any type inference
                                return {}, {}
                        vartype = UnionType(union_list)
                    elif isinstance(vartype, TypeType):
                        vartype = vartype.item
                    else:
                        # any other object whose type we don't know precisely
                        # for example, Any or Instance of type type
                        return {}, {}  # unknown type
                    yes_map, no_map = conditional_type_map(expr, vartype, type)
                    yes_map, no_map = map(convert_to_typetype, (yes_map, no_map))
                    return yes_map, no_map
            elif refers_to_fullname(node.callee, 'builtins.callable'):
                expr = node.args[0]
                if literal(expr) == LITERAL_TYPE:
                    vartype = type_map[expr]
                    return self.conditional_callable_type_map(expr, vartype)
        elif isinstance(node, ComparisonExpr) and experiments.STRICT_OPTIONAL:
            # Check for `x is None` and `x is not None`.
            is_not = node.operators == ['is not']
            if any(is_literal_none(n) for n in node.operands) and (
                    is_not or node.operators == ['is']):
                if_vars = {}  # type: TypeMap
                else_vars = {}  # type: TypeMap
                for expr in node.operands:
                    if (literal(expr) == LITERAL_TYPE and not is_literal_none(expr)
                            and expr in type_map):
                        # This should only be true at most once: there should be
                        # two elements in node.operands, and at least one of them
                        # should represent a None.
                        vartype = type_map[expr]
                        none_typ = [TypeRange(NoneTyp(), is_upper_bound=False)]
                        if_vars, else_vars = conditional_type_map(expr, vartype, none_typ)
                        break

                if is_not:
                    if_vars, else_vars = else_vars, if_vars
                return if_vars, else_vars
            # Check for `x == y` where x is of type Optional[T] and y is of type T
            # or a type that overlaps with T (or vice versa).
            elif node.operators == ['==']:
                first_type = type_map[node.operands[0]]
                second_type = type_map[node.operands[1]]
                if is_optional(first_type) != is_optional(second_type):
                    if is_optional(first_type):
                        optional_type, comp_type = first_type, second_type
                        optional_expr = node.operands[0]
                    else:
                        optional_type, comp_type = second_type, first_type
                        optional_expr = node.operands[1]
                    if is_overlapping_types(optional_type, comp_type):
                        return {optional_expr: remove_optional(optional_type)}, {}
            elif node.operators in [['in'], ['not in']]:
                expr = node.operands[0]
                left_type = type_map[expr]
                right_type = builtin_item_type(type_map[node.operands[1]])
                right_ok = right_type and (not is_optional(right_type) and
                                           (not isinstance(right_type, Instance) or
                                            right_type.type.fullname() != 'builtins.object'))
                if (right_type and right_ok and is_optional(left_type) and
                        literal(expr) == LITERAL_TYPE and not is_literal_none(expr) and
                        is_overlapping_types(left_type, right_type)):
                    if node.operators == ['in']:
                        return {expr: remove_optional(left_type)}, {}
                    if node.operators == ['not in']:
                        return {}, {expr: remove_optional(left_type)}
        elif isinstance(node, RefExpr):
            # Restrict the type of the variable to True-ish/False-ish in the if and else branches
            # respectively
            vartype = type_map[node]
            if_type = true_only(vartype)
            else_type = false_only(vartype)
            ref = node  # type: Expression
            if_map = {ref: if_type} if not isinstance(if_type, UninhabitedType) else None
            else_map = {ref: else_type} if not isinstance(else_type, UninhabitedType) else None
            return if_map, else_map
        elif isinstance(node, OpExpr) and node.op == 'and':
            left_if_vars, left_else_vars = self.find_isinstance_check(node.left)
            right_if_vars, right_else_vars = self.find_isinstance_check(node.right)

            # (e1 and e2) is true if both e1 and e2 are true,
            # and false if at least one of e1 and e2 is false.
            return (and_conditional_maps(left_if_vars, right_if_vars),
                    or_conditional_maps(left_else_vars, right_else_vars))
        elif isinstance(node, OpExpr) and node.op == 'or':
            left_if_vars, left_else_vars = self.find_isinstance_check(node.left)
            right_if_vars, right_else_vars = self.find_isinstance_check(node.right)

            # (e1 or e2) is true if at least one of e1 or e2 is true,
            # and false if both e1 and e2 are false.
            return (or_conditional_maps(left_if_vars, right_if_vars),
                    and_conditional_maps(left_else_vars, right_else_vars))
        elif isinstance(node, UnaryExpr) and node.op == 'not':
            left, right = self.find_isinstance_check(node.expr)
            return right, left

        # Not a supported isinstance check
        return {}, {}
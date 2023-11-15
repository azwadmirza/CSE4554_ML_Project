    def check_member_assignment(self, instance_type: Type, attribute_type: Type,
                                rvalue: Expression, context: Context) -> Tuple[Type, bool]:
        """Type member assigment.

        This is defers to check_simple_assignment, unless the member expression
        is a descriptor, in which case this checks descriptor semantics as well.

        Return the inferred rvalue_type and whether to infer anything about the attribute type
        """
        # Descriptors don't participate in class-attribute access
        if ((isinstance(instance_type, FunctionLike) and instance_type.is_type_obj()) or
                isinstance(instance_type, TypeType)):
            rvalue_type = self.check_simple_assignment(attribute_type, rvalue, context)
            return rvalue_type, True

        if not isinstance(attribute_type, Instance):
            rvalue_type = self.check_simple_assignment(attribute_type, rvalue, context)
            return rvalue_type, True

        if not attribute_type.type.has_readable_member('__set__'):
            # If there is no __set__, we type-check that the assigned value matches
            # the return type of __get__. This doesn't match the python semantics,
            # (which allow you to override the descriptor with any value), but preserves
            # the type of accessing the attribute (even after the override).
            if attribute_type.type.has_readable_member('__get__'):
                attribute_type = self.expr_checker.analyze_descriptor_access(
                    instance_type, attribute_type, context)
            rvalue_type = self.check_simple_assignment(attribute_type, rvalue, context)
            return rvalue_type, True

        dunder_set = attribute_type.type.get_method('__set__')
        if dunder_set is None:
            self.msg.fail("{}.__set__ is not callable".format(attribute_type), context)
            return AnyType(TypeOfAny.from_error), False

        function = function_type(dunder_set, self.named_type('builtins.function'))
        bound_method = bind_self(function, attribute_type)
        typ = map_instance_to_supertype(attribute_type, dunder_set.info)
        dunder_set_type = expand_type_by_instance(bound_method, typ)

        _, inferred_dunder_set_type = self.expr_checker.check_call(
            dunder_set_type, [TempNode(instance_type), rvalue],
            [nodes.ARG_POS, nodes.ARG_POS], context)

        if not isinstance(inferred_dunder_set_type, CallableType):
            self.fail("__set__ is not callable", context)
            return AnyType(TypeOfAny.from_error), True

        if len(inferred_dunder_set_type.arg_types) < 2:
            # A message already will have been recorded in check_call
            return AnyType(TypeOfAny.from_error), False

        return inferred_dunder_set_type.arg_types[1], False